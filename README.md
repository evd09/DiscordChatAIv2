# Discord AI Bot Setup Guide with Ollama

## Summary

The new Discord Ollama bot is a **feature-rich, customizable AI assistant** that brings powerful LLM chat, mini-games, leaderboards, emoji magic, and much more to your server—with full slash command support and safe NSFW controls.

## Prerequisites

- **Python 3.11+** (if not using Docker)
- **A Discord bot token**  
  Get your `DISCORD_TOKEN` from the [Discord Developer Portal](https://discord.com/developers/applications).
- **Your Discord server's ID**  
  Find your `GUILD_ID` [here](https://discord.id/).
- **[Ollama](https://ollama.com/) LLM server** running and accessible to the bot (local or remote)
- **Docker** (optional, but recommended for easy setup)


## 🚀 Setup & Usage

### 1. Clone the Repository

```bash 
git clone https://github.com/yourusername/discord-ollama-bot.git
cd discord-ollama-bot
```

### 2. Configure Environment
Create a .env file in the project root:
```env
DISCORD_TOKEN=your-discord-bot-token
OLLAMA_URL=http://localhost:11434/api/generate   # Or your remote Ollama server
OLLAMA_MODEL=hermes3                             # Or your Ollama model name
GUILD_ID=123456789012345678                      # Your Discord server's ID
```
### 3. Run with Docker (Recommended)
Build and start the bot:
```bash
docker compose build --no-cache
docker compose up
```

### 4. Or Run Locally (Python)
Make sure you have Python 3.11+ installed.
Install dependencies:
```bash
pip install -r requirements.txt
```
Start the bot:
```bash
python bot.py
```
### 5. Invite the Bot to Your Discord Server
- Use your app’s OAuth2 URL with the bot and applications.commands scopes.
- Add the bot to your server via the Discord Developer Portal.

### 6. Use the Bot
- Try slash commands like /help, /setcharacter, /trivia, etc. in your Discord server.
- NSFW commands/personas require an NSFW channel.

## Running the Bot

### ⚠️ Notes & Troubleshooting
- Slash commands can take 1-5 minutes to appear the first time (Discord caches them).
- After changing GUILD_ID, restart the bot for commands to update.
- All settings (scores, prompts) are stored locally. If using Docker, persist volumes as needed.
- For best performance, run Ollama LLM server on the same local network or a fast connection.

🛑 Stopping the Bot

With Docker:
```bash
docker compose down
```
Running locally:
```bash
Ctrl+C
```
---
## Key Differences & Improvements

### 1. **Modern Discord API Usage**
- **Old:** Uses `discord.Client` and classic on_message event handling.
- **New:** Uses `discord.ext.commands.Bot` and full support for **slash commands** (Discord application commands), which are now Discord’s preferred method for bots.

---

### 2. **Contextual Memory**
- **Old:** Maintains a rolling history per channel for response context, but not per-user.
- **New:** Maintains **per-channel and per-user conversation history** (for better context and future support of persistent memory, Q&A recall, and AI character switching).

---

### 3. **Dynamic Prompt Control**
- **Old:** Hardcoded prompt, always uses a simple "Context:\n..." for every LLM request.
- **New:** Lets server admins and users:
  - `/setprompt <text>` — Set the current system prompt
  - `/showprompt` — See current system prompt
  - `/resetprompt` — Revert to default prompt
  - **Prompt changes persist** across bot restarts.

---

### 4. **AI Persona/Character Switching**
- **Old:** No character/persona system—only a single default bot “voice.”
- **New:** **Multiple built-in AI personas**, including:
  - SFW: meme, wise sage, therapist, Shakespeare, anime waifu, etc.
  - **NSFW characters:** (sexy nurse, dom, etc.) only available in NSFW channels.
  - `/setcharacter` lets each user pick their own AI “character” for DMs and @mentions.
  - `/mycharacter` shows your current persona.

---

### 5. **Mini-Games & Fun**
- **Old:** None.
- **New:** **Mini-games with leaderboards:**
  - `/trivia` — General trivia, with answer buttons, scoring, and leaderboard
  - `/nsfwtrivia` — Urban Dictionary trivia, only in NSFW channels
  - `/trivialeaderboard` — See who’s best/worst at trivia
  - `/8ball <question>` — Magic 8-ball
  - `/roll` — Dice roller

---

### 6. **Leaderboards & Scoring**
- **Old:** None.
- **New:** Persistent trivia stats saved to disk (per-user: correct, wrong, win rate).
  - Top 5 and Bottom 5 users shown via `/trivialeaderboard`.

---

### 7. **NSFW Command and Persona Safety**
- **Old:** No safety checks; no support for NSFW content.
- **New:** NSFW commands and personas **require** Discord NSFW channels for usage.
  - Protects users and follows Discord guidelines.

---

### 8. **Emoji Reactions & Sentiment**
- **Old:** Chaotic, sometimes 1–20 random emoji reactions, contextually selected, but no extensible emoji handling.
- **New:** Smarter emoji selection with sentiment analysis, emoji library, and consistent reactions (2 per message).

---

### 9. **Slash Command Help & User Guidance**
- **Old:** No `/help` command.
- **New:** `/help` command lists all features, including mini-games and persona switching, and clarifies which features are NSFW.

---

### 10. **Stability & Maintainability**
- **Old:** Monolithic, all logic in one script, manual request handling.
- **New:**
  - Modular, modern code with clear function separation
  - Use of `aiohttp` for async HTTP calls (faster and more scalable)
  - **Logging** for debug and info
  - Conversation and score logs written to disk
  - Uses `.env` for configuration, not hardcoded

---

### 11. **Docker & Deployment**
- **Old:** No explicit Docker support.
- **New:** Includes:
  - `Dockerfile`
  - `docker-compose.yml`
  - Volume for persistent logs
  - Easy local or containerized deployment

---

### 12. **Extensible for Future Features**
- Prompt history with undo/voting (planned)
- Per-user long-term memory (planned)
- More mini-games and integrations

---

## Sample Table of New Commands

| Command               | Description                                      |
|:----------------------|:-------------------------------------------------|
| `/setprompt <text>`   | Set a custom system prompt for the AI            |
| `/showprompt`         | Show the current prompt                          |
| `/resetprompt`        | Reset to default prompt                          |
| `/setcharacter`       | Pick your own AI persona                         |
| `/mycharacter`        | Show your current persona                        |
| `/help`               | Show all bot commands and character list         |
| `/trivia`             | Play SFW trivia game                             |
| `/nsfwtrivia`         | Play NSFW Urban Dictionary trivia                |
| `/trivialeaderboard`  | Show trivia stats/leaderboard                    |
| `/8ball <question>`   | Magic 8-ball prediction                          |
| `/roll`               | Roll a dice                                      |

---

**Ready for the next level of Discord AI fun!**
