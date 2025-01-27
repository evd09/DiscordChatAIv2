# Discord Bot Setup Guide with Ollama

A simple Discord bot powered by local Ollama models for chat interactions.

## Prerequisites

- **Python** installed on your machine
- **Ollama** installed from [Ollama's official website](https://ollama.ai/)
- A **Discord account** and server

## Setup Steps

1. Install Ollama and pull the model:
   ```bash
   ollama pull hermes3
   ```

2. Create Discord Bot:
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Click "New Application" and name it
   - Go to "Bot" tab, click "Add Bot"
   - Copy your bot token

3. Set up the bot:
   ```bash
   git clone https://github.com/gnukeith/DiscordChatAI.git
   cd DiscordChatAI
   ```

4. Create a `.env` file:
   ```env
   DISCORD_TOKEN=your_bot_token_here
   ```

5. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Bot

1. Start the bot:
   ```bash
   python your_bot_file.py
   ```

2. Test by mentioning the bot in Discord: `@YourBotName hello`

## Notes
- Bot responds to mentions only
- Conversations are logged in `conversations.log`