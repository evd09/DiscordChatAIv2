# 🤖 Discord AI Meme Bot

A powerful, AI-enhanced Discord bot that:
- Chats using Ollama models (like Hermes)
- Responds with emoji reactions based on sentiment
- Greets new users with AI-generated jokes
- Auto-replies in threads for long responses
- Logs activity with rotating logs
- Dockerized for easy deployment

---

## 🚀 Features

| Feature                        | Description |
|-------------------------------|-------------|
| 🧠 AI Chat                    | Uses Ollama + Hermes (or custom model) for conversational replies |
| 😄 Emoji Reactions            | Responds with mood-based emojis using sentiment analysis |
| 💬 Contextual Memory          | Remembers recent messages per channel for better AI replies |
| 🧵 Auto-Threading             | Long replies spawn a thread to avoid message limit errors |
| 🐳 Docker Support             | Easily containerized for deployment via Docker Compose |

---

## 📦 File Structure
```text
Nebula/
│
├── bot.py                # Main bot launcher and root command logic
├── requirements.txt      # List of Python dependencies for pip install
├── Dockerfile            # Build instructions for Docker (single-container)
├── docker-compose.yml    # Docker Compose for multi-container setup
├── .env                  # Main environment variables (bot token, model, guild ID)
├── data/ 
│   └── botdata.db        # A database file used to store persistent data.
├── logs/                 
│   └── bot.log           # The main log file for your bot.
├── cogs/             
│   ├── character.py      # Handles all "character/personality" commands and logic.
│   ├── fun.py            # Contains fun commands like jokes, 8ball, memes, etc.
│   └── trivia.py         # Commands and logic for running trivia games.
├── helpers/              
│   ├── personalities.py  # The definitions and descriptions for each AI personality/character.
│   └── utils.py          # Helper functions used by multiple parts of your bot.
│   └── db.py             # Handles connecting to and working with your bot’s database.
└── README.md             # You’re here! Main documentation and run instructions
```
🐳 Docker Deployment for Nebula
1. Create directory for config files
```
mkdir NebulaAI
cd NebulaAI
```

2. Create Required Folders and .env File
```
mkdir sounds data logs
mkdir -p sounds/entrances
mkdir -p sounds/beeps
nano .env
```

```
DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN
OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=hermes3
```

3. Run with Docker CLI
```
sudo docker pull ghcr.io/evd09/memebot:latest
```
4. Docker Compose (Recommended for Easy Updates)
```
services:
  discord-bot:
    image: ghcr.io/evd09/nebulaai:latest   
    container_name: NebulaAI
    restart: unless-stopped
    env_file:
      - .env         # Loads your Discord token and other environment variables
    volumes:
      - ./logs:/app/logs    # Mount local logs folder to container
      - ./data:/app/data    # Mount local data folder to container
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "5"
```

### Start the bot:
```
sudo docker compose pull
sudo docker compose up -d
```

### To upgrade:
```
sudo docker compose down
sudo docker compose pull
sudo docker compose up -d
```

## ✅ Commands & Triggers
🧠 AI Chat

    Mention the bot in a message to trigger a reply:
        @BotName what do you think of pineapples on pizza?

## 🤖 Nebula AI Bot — Command Reference

| Command                   | Description                                   |
|---------------------------|-----------------------------------------------|
| `/character` 				| Set your AI character/persona style           |
| `/8ball <question>`       | Magic 8-ball answers your yes/no question 	|
| `/fortune`        	    | Receive a random fortune!   					|
| `/roast`   				| Get a roast, or roast someone else!         	|
| `/trivia`                 | Play a multiple-choice trivia game            |
| `/nsfwtrivia`             | Play a NSFW (adult) trivia game        		|
| `/trivialeaderboard`      | Show the top and bottom trivia performers 	|
| `/help`                   | Show this help table                      	|


## 📧 Feedback / Suggestions

Have ideas or issues? Open a GitHub issue or ping me in your server! ✨


