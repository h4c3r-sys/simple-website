# How to Deploy Scam Blocker Bot

This guide explains how to deploy the Scam Blocker Discord bot to an online server (VPS) like DigitalOcean, AWS, Linode, or Vultr.

## 1. Prerequisites

Before you begin, ensure you have:

1.  **A Virtual Private Server (VPS):** A basic Linux server (Ubuntu 20.04/22.04 recommended). The bot is lightweight, so 1GB-2GB RAM is sufficient.
2.  **Discord Developer Account:** Access to the [Discord Developer Portal](https://discord.com/developers/applications).
3.  **API Keys (Optional):** OpenAI API Key or Google Gemini API Key if you want to use the AI features.

---

## 2. Discord Application Setup

1.  Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2.  Click **"New Application"** and give it a name (e.g., "Scam Blocker").
3.  Go to the **"Bot"** tab on the left sidebar.
4.  Click **"Reset Token"** to generate your `DISCORD_TOKEN`. **Save this for later.**
5.  **Enable Privileged Intents** (Scroll down on the Bot page):
    *   ✅ **Message Content Intent** (Required for scanning messages)
    *   ✅ **Server Members Intent** (Required for banning/kicking)
    *   *(Presence Intent is not required)*
6.  Go to the **"OAuth2" -> "URL Generator"** tab.
    *   Select Scope: `bot`
    *   Select Bot Permissions:
        *   `View Channels`
        *   `Send Messages`
        *   `Embed Links`
        *   `Read Message History`
        *   `Manage Messages`
        *   `Moderate Members`
        *   `Kick Members`
        *   `Ban Members`
        *   `Manage Channels` (For /safetest)
        *   `Manage Webhooks` (For /safetest)
7.  Copy the generated URL and use it to invite the bot to your server.

---

## 3. Server Setup (Ubuntu)

Connect to your VPS via SSH:

```bash
ssh root@your_server_ip
```

### Install Docker & Docker Compose

Run the following commands to install Docker:

```bash
# Update package list
sudo apt update
sudo apt install -y ca-certificates curl gnupg

# Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add the repository
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

---

## 4. Bot Deployment

### 1. Clone the Repository

Upload your code to the server. You can use Git (recommended) or SCP.

```bash
# Example if using git
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

### 2. Configure Environment

Create the `.env` file from the example:

```bash
cp .env.example .env
nano .env
```

Fill in your details:

```ini
DISCORD_TOKEN=your_token_from_step_2
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secure_password_here
POSTGRES_DB=discord_bot_db

# Optional AI Keys (Leave empty if using local machine learning)
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...

# Optional: Default target server for /safetest
SAFETEST_SOURCE_GUILD_ID=
```

Press `Ctrl+O`, `Enter` to save, and `Ctrl+X` to exit.

### 3. Start the Bot

Run the bot using Docker Compose. This builds the container and starts the database.

```bash
docker compose up --build -d
```

*Note: If you installed the older `docker-compose` (standalone), use `docker-compose up --build -d`.*

### 4. Verify It's Running

Check the logs to ensure everything started correctly:

```bash
./scripts/view_logs.sh
# OR
docker compose logs -f bot
```

You should see:
> `INFO:bot.main:Commands synced.`
> `INFO:discord.client:logging in using static token`
> `INFO:discord.gateway:Shard ID None has connected to Gateway`

---

## 5. Usage & Maintenance

### Common Commands

*   `/setup [channel]` - Set the log channel.
*   `/scan [period]` - Scan history and detect spam words.
*   `/scanlogs [period]` - Scan and generate a debug file.
*   `/safetest [target_id]` - Clone the current server to a test server.
*   `!sync` - Force sync commands if they don't appear (Admin only).

### Updating the Bot

If you change the code, deploy the updates:

```bash
# Pull changes (if using git)
git pull

# Rebuild and restart
docker compose up --build -d
```

### Database Backups

To back up your banned words and message history:

```bash
docker compose exec -t db pg_dump -U postgres discord_bot_db > backup_$(date +%F).sql
```

To restore:

```bash
cat backup.sql | docker compose exec -T db psql -U postgres -d discord_bot_db
```
