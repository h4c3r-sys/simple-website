# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-05-24

### Added

#### Core Features
- **Scam Detection Engine:** Implemented `SpamAnalyzer` using a hybrid approach:
    - **Cold Start Heuristics:** Uses seed words (e.g., "nitro", "steam") and patterns (links, entropy) to identify potential spam without pre-labeled data.
    - **Machine Learning:** Uses local TF-IDF (Term Frequency-Inverse Document Frequency) to find unique keywords in the "potential spam" set.
    - **LLM Integration:** Supports OpenAI (GPT-3.5) and Google Gemini (2.0-Flash/1.5-Flash) for advanced keyword extraction if API keys are provided.
- **Active Moderation:**
    - **Auto-Delete:** Removes messages containing banned words (using regex for whole-word matching to avoid false positives).
    - **Auto-Timeout:** Times out users for 1 hour upon violation.
    - **Interactive Logs:** Posts violation details to a configured channel with buttons to Ban, Kick, Ignore, or Remove Timeout.

#### Commands
- `/scan [period]`: Scans channel history, analyzes messages, and suggests banned words for admin approval.
- `/safetest [target_id]`: Clones messages from the current server to a target test server using Webhooks to safely verify bot behavior.
- `/scanlogs [period]`: Runs a scan and generates a downloadable debug log file (capturing SQL queries and API responses).
- `/setup [channel]`: Configures the logging channel for the server.
- `/role [add/remove]`: Manages bot permissions (Admin/Mod roles).
- `!sync`: Text command to force-sync slash commands globally.

#### Access Control (RBAC)
- **Role Management:**
    - **Automatic Discovery:** Automatically recognizes roles named "admin", "owner", "mod", "staff", etc.
    - **Manual Configuration:** Allows assigning specific roles as Bot Admins (can run commands) or Mods (exempt from bans).
    - **Database Storage:** Persists role configurations in PostgreSQL.

#### Infrastructure
- **Dockerized Setup:** Complete `Dockerfile` and `docker-compose.yml` for easy deployment.
- **Database:** PostgreSQL integration via SQLAlchemy (async) for storing messages, banned words, and settings.
- **Maintenance Scripts:** Added `scripts/view_logs.sh` and `scripts/access_db.sh` for easy debugging.
- **Documentation:** Added `README.md` (setup & permissions) and `how_to_deploy.md` (VPS guide).

### Fixed
- **Gemini API:** Fixed "404 Model Not Found" by updating to `gemini-2.0-flash` with fallback to `1.5-flash`.
- **OpenAI API:** Updated client instantiation to match v1.0+ syntax.
- **SafeTest:** Adjusted `on_message` logic to scan Webhooks (required for testing) while still ignoring standard bots.
