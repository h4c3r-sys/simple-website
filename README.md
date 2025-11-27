# Scam Blocker Discord Bot

A Discord bot that uses machine learning (TF-IDF analysis) to identify potential scam keywords from chat history and enforce bans on those keywords.

## Features

- **Automated Scanning (`/scan`)**: Fetches messages from the server's history, analyzes them for spam patterns, and suggests a list of banned words.
- **Machine Learning**: Uses a local `scikit-learn` model to compare "potential spam" (identified via heuristics) against normal conversation to find distinctive scam keywords.
- **Active Protection**: Automatically deletes messages containing banned words and times out the user for 1 hour.
- **Moderation Logs**: detailed logs with buttons to Ban, Kick, Ignore, or Remove Timeout.
- **Database**: Stores configuration and banned words in a PostgreSQL database.
- **Dockerized**: Easy deployment with Docker Compose.

## Setup

1. **Prerequisites**
   - Docker and Docker Compose installed.
   - A Discord Bot Token (from the [Discord Developer Portal](https://discord.com/developers/applications)).

2. **Configuration**
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and paste your `DISCORD_TOKEN`.
   - (Optional) Add `OPENAI_API_KEY` or `GEMINI_API_KEY` to use advanced AI analysis instead of local machine learning.

3. **Required Permissions**
   To function correctly, the bot requires the following permissions and intents:

   **Bot Permissions (Invite Link):**
   - **View Channels**: Required to read messages in channels.
   - **Send Messages**: Required to send logs and responses.
   - **Embed Links**: Required for formatted logs.
   - **Read Message History**: Critical for the `/scan` command to learn from past data.
   - **Manage Messages**: Required to delete messages containing banned words.
   - **Moderate Members**: Required to timeout users.
   - **Kick Members**: Required for the "Kick" button in violation logs.
   - **Ban Members**: Required for the "Ban" button in violation logs.
   - **Manage Channels**: Required for the `/safetest` command to create test channels.
   - **Manage Webhooks**: Required for the `/safetest` command to clone messages.

   **Privileged Intents (Enable in Developer Portal):**
   - **Message Content Intent**: REQUIRED. The bot needs this to read message text for scanning and checking against the ban list.
   - **Server Members Intent**: REQUIRED. Needed to perform member-related actions (like fetching member objects for bans/kicks).

4. **Run the Bot**
   ```bash
   docker-compose up --build -d
   ```

4. **Bot Setup in Discord**
   - Invite the bot to your server.
   - Run `/setup` to configure the logging channel (optional, defaults to current channel).
   - Run `/scan [period]` (e.g., `/scan Last Month`) to start learning.
   - Approve the suggested ban words.

## Architecture

- **`bot/main.py`**: Entry point, command handlers, and event listeners.
- **`bot/analyzer.py`**: The "brain". Contains the `SpamAnalyzer` class that performs text analysis.
- **`bot/models.py`**: Database schemas (SQLAlchemy).
- **`bot/database.py`**: Async database connection logic.

## Logic Details

The bot solves the "Cold Start" problem (learning what spam looks like without a pre-labeled dataset) by:
1. Fetching recent messages.
2. Applying heuristics (links + known spam seed words) to tentatively label a subset of messages as "Potential Spam".
3. Using TF-IDF (Term Frequency-Inverse Document Frequency) to find other words that appear frequently in that "Potential Spam" set but rarely in the "Clean" set.
4. Suggesting these distinctive words to the admin.
