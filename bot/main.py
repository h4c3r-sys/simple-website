import discord
from discord.ext import commands
from discord import app_commands
from bot.database import get_db, init_db, AsyncSessionLocal
from bot.models import GuildSettings, BannedWord, StoredMessage
from bot.analyzer import SpamAnalyzer
from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert
import pandas as pd
import datetime
import logging
import asyncio
import os
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScamBlockerBot(commands.Bot):
    """
    Main Bot Class.
    Handles command synchronization and database initialization on startup.
    """
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True # Required to read message content for scanning/protection
        intents.members = True # Needed to kick/ban members
        super().__init__(command_prefix="!", intents=intents)
        self.session_maker = AsyncSessionLocal

    async def setup_hook(self):
        """
        Executed when the bot starts up.
        Initializes the database and syncs slash commands with Discord.
        """
        # Initialize DB tables
        await init_db()
        # Sync commands to the server (globally)
        await self.tree.sync()
        logger.info("Commands synced.")

bot = ScamBlockerBot()

# --- UTILS ---
async def get_log_channel(guild, session):
    """
    Retrieves the configured log channel for a guild from the database.
    """
    result = await session.execute(select(GuildSettings).where(GuildSettings.guild_id == guild.id))
    settings = result.scalars().first()
    if settings and settings.log_channel_id:
        return guild.get_channel(settings.log_channel_id)
    return None

async def log_action(guild, session, embed):
    """
    Sends a log embed to the configured channel.
    """
    channel = await get_log_channel(guild, session)
    if channel:
        try:
            return await channel.send(embed=embed)
        except discord.errors.Forbidden:
            logger.warning(f"Missing permissions to send logs in {channel.name}")
    return None

# --- VIEWS ---

class ApprovalView(discord.ui.View):
    """
    View displayed after a Scan.
    Allows admins to Approve or Disapprove the suggested ban list.
    """
    def __init__(self, suggested_words, session_maker):
        super().__init__(timeout=None)
        self.suggested_words = suggested_words
        self.session_maker = session_maker

    @discord.ui.button(label="Approve All", style=discord.ButtonStyle.green)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        async with self.session_maker() as session:
            # Batch insert suggested words into the database
            for word in self.suggested_words:
                stmt = insert(BannedWord).values(guild_id=interaction.guild_id, word=word).on_conflict_do_nothing()
                await session.execute(stmt)
            await session.commit()

        await interaction.followup.send(f"✅ Added {len(self.suggested_words)} words to the ban list.", ephemeral=True)
        self.stop()

    @discord.ui.button(label="Disapprove (Cancel)", style=discord.ButtonStyle.red)
    async def disapprove(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("❌ Cancelled. No words added.", ephemeral=True)
        self.stop()

class ViolationView(discord.ui.View):
    """
    View displayed on a violation log.
    Provides buttons for admins to take further action on a user.
    """
    def __init__(self, user_id, message_content):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.message_content = message_content

    @discord.ui.button(label="Ban User", style=discord.ButtonStyle.danger)
    async def ban_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.guild.ban(discord.Object(id=self.user_id), reason="Scam/Spam detected")
            await interaction.response.send_message(f"🔨 Banned user <@{self.user_id}>.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Missing permissions to ban.", ephemeral=True)

    @discord.ui.button(label="Kick User", style=discord.ButtonStyle.danger)
    async def kick_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            member = interaction.guild.get_member(self.user_id)
            if member:
                await member.kick(reason="Scam/Spam detected")
                await interaction.response.send_message(f"👢 Kicked user <@{self.user_id}>.", ephemeral=True)
            else:
                await interaction.response.send_message("❌ User not found in server.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Missing permissions to kick.", ephemeral=True)

    @discord.ui.button(label="Ignore (False Positive)", style=discord.ButtonStyle.secondary)
    async def ignore_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("⚠️ Marked as ignored (Note: This does not unban the word automatically).", ephemeral=True)

    @discord.ui.button(label="Remove Timeout", style=discord.ButtonStyle.success)
    async def remove_timeout(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            member = interaction.guild.get_member(self.user_id)
            if member:
                await member.timeout(None, reason="Admin removed timeout")
                await interaction.response.send_message(f"✅ Removed timeout for <@{self.user_id}>.", ephemeral=True)
            else:
                await interaction.response.send_message("❌ User not found.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Missing permissions to remove timeout.", ephemeral=True)

# --- COMMANDS ---

@bot.tree.command(name="setup", description="Configure the bot (e.g., log channel)")
@app_commands.checks.has_permissions(administrator=True)
async def setup(interaction: discord.Interaction, log_channel: discord.TextChannel = None):
    """
    Sets the channel where violation logs will be sent.
    """
    async with bot.session_maker() as session:
        # Check if settings exist
        result = await session.execute(select(GuildSettings).where(GuildSettings.guild_id == interaction.guild_id))
        settings = result.scalars().first()

        target_channel_id = log_channel.id if log_channel else interaction.channel_id

        if not settings:
            settings = GuildSettings(guild_id=interaction.guild_id, log_channel_id=target_channel_id)
            session.add(settings)
        else:
            settings.log_channel_id = target_channel_id

        await session.commit()

    await interaction.response.send_message(f"✅ Setup complete! Logging to <#{target_channel_id}>.", ephemeral=True)

@bot.tree.command(name="safetest", description="Clone messages from a target server to this server for safe testing")
@app_commands.describe(target_server_id="ID of the server to copy messages from (Optional if set in env)")
@app_commands.checks.has_permissions(administrator=True)
async def safetest(interaction: discord.Interaction, target_server_id: str = None):
    """
    Copies messages from a target server to the current server using Webhooks.
    This creates a safe environment to test the bot's spam detection on real data.
    """
    await interaction.response.defer(thinking=True)

    # Logic to prioritize Argument > Env Variable
    target_id_str = target_server_id
    if not target_id_str:
        target_id_str = os.getenv("SAFETEST_SOURCE_GUILD_ID")

    if not target_id_str:
        await interaction.followup.send("❌ No target server specified. Please provide an ID or set SAFETEST_SOURCE_GUILD_ID in .env")
        return

    try:
        target_guild_id = int(target_id_str)
        target_guild = bot.get_guild(target_guild_id)

        if not target_guild:
            # Try to fetch if not in cache (requires bot to be in that server)
            try:
                target_guild = await bot.fetch_guild(target_guild_id)
            except discord.Forbidden:
                await interaction.followup.send(f"❌ I am not in the target server ({target_guild_id}) or lack permissions to view it.")
                return
            except discord.NotFound:
                 await interaction.followup.send("❌ Target server not found.")
                 return

    except ValueError:
        await interaction.followup.send("❌ Invalid Server ID format.")
        return

    await interaction.followup.send(f"🔄 Starting Safe Test Clone from **{target_guild.name}**. This may take a while...")
    logger.info(f"Starting safetest clone from {target_guild.name} ({target_guild.id}) to {interaction.guild.name}")

    count = 0
    # Iterate through text channels in the target guild
    # Note: Fetching channels from a guild we just fetched might need API call
    try:
        channels = await target_guild.fetch_channels()
    except Exception as e:
        logger.error(f"Failed to fetch channels: {e}")
        await interaction.channel.send(f"❌ Error fetching channels: {e}")
        return

    current_guild = interaction.guild

    for channel in channels:
        if not isinstance(channel, discord.TextChannel):
            continue

        # 1. Create matching channel in current guild if not exists
        target_channel_name = channel.name
        dest_channel = discord.utils.get(current_guild.text_channels, name=target_channel_name)

        if not dest_channel:
            try:
                dest_channel = await current_guild.create_text_channel(name=target_channel_name, reason="Safe Test Clone")
                await asyncio.sleep(1) # Avoid rate limits
            except discord.Forbidden:
                logger.warning(f"Cannot create channel {target_channel_name}")
                continue

        # 2. Create Webhook in destination channel
        webhook = None
        try:
            webhooks = await dest_channel.webhooks()
            if webhooks:
                webhook = webhooks[0]
            else:
                webhook = await dest_channel.create_webhook(name="SafeTest Clone Hook")
        except Exception as e:
            logger.warning(f"Failed to manage webhook in {dest_channel.name}: {e}")
            continue

        # 3. Fetch and Repost Messages
        # We limit to 500 messages per channel to prevent infinite loops and hour-long waits,
        # unless it's critical to have ALL. Given "copy all messages", we try a larger batch but safe.
        try:
            async for msg in channel.history(limit=500, oldest_first=False):
                if not msg.content:
                    continue

                # Send via Webhook
                try:
                    await webhook.send(
                        content=msg.content,
                        username=msg.author.name,
                        avatar_url=msg.author.display_avatar.url,
                        wait=True # Wait to respect rate limits
                    )
                    count += 1
                    # Small sleep to be nice to API
                    await asyncio.sleep(0.5)
                except Exception as e:
                    logger.warning(f"Failed to copy message: {e}")
        except discord.Forbidden:
            logger.warning(f"Cannot read history from {channel.name}")
            continue

        await asyncio.sleep(2) # Buffer between channels

    await interaction.channel.send(f"✅ Safe Test Clone Complete! Copied {count} messages.")

@bot.tree.command(name="scan", description="Scan messages to identify scam keywords")
@app_commands.describe(period="Time period to scan")
@app_commands.choices(period=[
    app_commands.Choice(name="Last Day", value="1d"),
    app_commands.Choice(name="Last Week", value="7d"),
    app_commands.Choice(name="Last Month", value="30d"),
    app_commands.Choice(name="Last Year", value="365d"),
    app_commands.Choice(name="All Time", value="all"),
])
@app_commands.checks.has_permissions(administrator=True)
async def scan(interaction: discord.Interaction, period: app_commands.Choice[str]):
    """
    Scans the channel history for messages, saves them to DB, and triggers the SpamAnalyzer.
    """
    await interaction.response.defer(thinking=True)

    # Calculate cutoff date based on user selection
    now = datetime.datetime.now(datetime.timezone.utc)
    cutoff = None
    if period.value != "all":
        days = int(period.value[:-1])
        cutoff = now - datetime.timedelta(days=days)

    logger.info(f"Starting scan for guild {interaction.guild.name} ({interaction.guild.id}) - Period: {period.name}")

    # Fetch messages
    scanned_count = 0
    messages_data = []

    async with bot.session_maker() as session:
        for channel in interaction.guild.text_channels:
            try:
                # We fetch history. Note: This can be slow.
                # We set a high safety cap to avoid hanging on massive channels.
                limit = 10000
                if period.value == "all":
                    limit = 20000

                async for msg in channel.history(limit=limit, after=cutoff):
                    if msg.content:
                        # Save to DB for future training/history
                        stmt = insert(StoredMessage).values(
                            message_id=msg.id,
                            guild_id=interaction.guild_id,
                            channel_id=msg.channel.id,
                            author_id=msg.author.id,
                            content=msg.content,
                            created_at=msg.created_at,
                            is_bot=msg.author.bot
                        ).on_conflict_do_nothing()
                        await session.execute(stmt)

                        messages_data.append({
                            'content': msg.content,
                            'is_bot': msg.author.bot,
                            'author_id': msg.author.id
                        })
                        scanned_count += 1
            except discord.Forbidden:
                continue
            except Exception as e:
                logger.error(f"Error scanning channel {channel.name}: {e}")

        await session.commit()

    if not messages_data:
        await interaction.followup.send("⚠️ No messages found in the specified period.")
        return

    # Run Analysis
    df = pd.DataFrame(messages_data)
    analyzer = SpamAnalyzer()

    # Run analysis in a thread executor to avoid blocking the main Discord event loop
    loop = asyncio.get_running_loop()
    suggested_words = await loop.run_in_executor(None, analyzer.analyze_and_suggest_bans, df)

    if not suggested_words:
        await interaction.followup.send(f"✅ Scan complete ({scanned_count} messages). No obvious spam patterns found.")
        return

    # Present Results
    embed = discord.Embed(title="🛡️ Scan Results: Proposed Banned Words", color=discord.Color.orange())
    embed.description = "The following words were identified as potential spam keywords based on statistical analysis.\n\n" + \
                        ", ".join([f"`{w}`" for w in suggested_words])

    view = ApprovalView(suggested_words, bot.session_maker)

    # Send to console channel if exists, else followup
    async with bot.session_maker() as session:
        log_chan = await get_log_channel(interaction.guild, session)

    if log_chan:
        await log_chan.send(embed=embed, view=view)
        await interaction.followup.send(f"✅ Scan complete. Results sent to {log_chan.mention}.")
    else:
        await interaction.followup.send(embed=embed, view=view)

# --- EVENTS ---

@bot.event
async def on_message(message):
    """
    Active protection listener.
    Checks every new message against the database of BannedWords.
    """
    # Ignore DMs
    if not message.guild:
        return

    # Check if author is bot.
    # CRITICAL CHANGE FOR SAFETEST: We MUST allow Webhooks to be scanned,
    # because /safetest uses webhooks to simulate users.
    # Typically message.author.bot is True for webhooks.
    # We check if it's a specific bot user, but allow webhooks.
    if message.author.bot and not message.webhook_id:
        return

    # Check for banned words
    async with bot.session_maker() as session:
        # Get banned words for this guild
        result = await session.execute(select(BannedWord.word).where(BannedWord.guild_id == message.guild.id))
        banned_words = [row[0] for row in result.all()]

        if not banned_words:
            return

        content_lower = message.content.lower()

        detected = False
        detected_word = ""
        for word in banned_words:
            # Use regex to match whole words only to avoid the Scunthorpe problem
            # e.g., banning "hack" should not ban "hackathon"
            # (?<!\w) means "not preceded by a word character"
            # (?!\w) means "not followed by a word character"
            pattern = r"(?<!\w)" + re.escape(word.lower()) + r"(?!\w)"
            if re.search(pattern, content_lower):
                detected = True
                detected_word = word
                break

        if detected:
            # Action!
            try:
                await message.delete()
            except discord.NotFound:
                pass # Already deleted
            except discord.Forbidden:
                logger.warning("Failed to delete message: Missing permissions")

            # Timeout 1h (Only works on real members, not webhooks)
            if isinstance(message.author, discord.Member):
                try:
                    duration = datetime.timedelta(hours=1)
                    await message.author.timeout(duration, reason=f"Used banned word: {detected_word}")
                except discord.Forbidden:
                    logger.warning("Failed to timeout user: Missing permissions")

            # Log
            embed = discord.Embed(title="🚨 Scam/Spam Detected", color=discord.Color.red(), timestamp=datetime.datetime.now())
            embed.add_field(name="User", value=f"{message.author.mention} (`{message.author.id}`)", inline=True)
            embed.add_field(name="Detected Word", value=f"`{detected_word}`", inline=True)
            embed.add_field(name="Message Content", value=message.content[:1000], inline=False) # Discord limit 1024

            view = ViolationView(message.author.id, message.content)

            log_message = await log_action(message.guild, session, embed)
            if log_message:
                await log_message.edit(view=view)

    # Process commands if any (though we use slash commands mostly)
    await bot.process_commands(message)

# Run
if __name__ == "__main__":
    import os
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("DISCORD_TOKEN not set!")
    else:
        bot.run(token)
