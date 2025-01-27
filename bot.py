import discord
import requests
import json
import os

# Initialize Discord bot
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Ollama API configuration
ollama_url = "http://localhost:11434/api/generate"
model_name = "hermes3"

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user in message.mentions:
        prompt = message.content.replace(f'<@{client.user.id}>', '').strip()
        
        try:
            # Generate response using Ollama API
            data = {
                "model": model_name,
                "prompt": prompt,
                "stream": False
            }
            response = requests.post(ollama_url, headers={"Content-Type": "application/json"}, data=json.dumps(data))
            response.raise_for_status()
            
            response_text = json.loads(response.text)['response']
            
            # Log the conversation
            with open('conversations.log', 'a') as f:
                f.write(f"User: {prompt}\nBot: {response_text}\n")
            
            await message.channel.send(response_text)
            
        except Exception as e:
            print(f"Error: {e}")
            await message.channel.send("Sorry, I'm having trouble responding right now.")

# Run the bot
client.run(os.getenv('DISCORD_TOKEN'))
