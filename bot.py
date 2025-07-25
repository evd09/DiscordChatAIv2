import discord
import requests
import json
import os
import datetime
from dotenv import load_dotenv
import random
import re

# Load environment variables from .env file
load_dotenv()

# Get the Discord bot token from environment variables
TOKEN = os.getenv('DISCORD_TOKEN')
print(f"Token loaded: {'Found token' if TOKEN else 'No token found'}")

# Initialize Discord bot with necessary intents
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
client = discord.Client(intents=intents)

# Ollama API configuration
ollama_url = "http://localhost:11434/api/generate"
model_name = "hermes3"

# Emoji categories used for reactions
HAPPY_EMOJIS = ['😊', '😄', '😃', '🥰', '😘', '😋', '😍', '🤗', '🌟', '✨', '💫', '⭐']
SAD_EMOJIS = ['😢', '😭', '🥺', '😔', '🚪', '💔', '😿', '🫂', '🦀']
PLAYFUL_EMOJIS = ['😜', '🤪', '😝', '😋', '🤭', '🙈', '🙉', '🙊', '🐱', '🐰', '🦊', '🐼']
COOL_EMOJIS = ['😎', '👶️', '🔥', '💯', '🆒', '🤙', '👑', '💪', '✌️', '🎮', '🎯', '🎪']
LOVE_EMOJIS = ['❤️', '🧡', '💛', '💚', '💙', '💜', '🧽', '🖤', '💝', '💖', '💗', '💓']
SPOOKY_EMOJIS = ['💀', '👻', '🎃', '🦷', '🕷️', '🕸️', '🧟‍♂️', '🧟‍♀️', '👺', '👹', '😈', '🤡']
THINKING_EMOJIS = ['🤔', '🧐', '💭', '💡', '🎯', '📚', '🔍', '💻', '📝']
MISC_EMOJIS = ['🌈', '🎨', '🎭', '🎪', '🎡', '🎢', '🎠', '🌸', '🌺', '🌷', '🌹', '🍀']

# Dictionary to store message history per channel
message_history = {}
HISTORY_LENGTH = 10

# Helper: decide if bot should respond to message
def should_respond(message_content, bot_name):
    keywords = ["hey", "hello", "yo", "chat", bot_name.lower()]
    return any(kw in message_content.lower() for kw in keywords)

# Helper: build a context string from message history
def get_conversation_context(channel_id):
    history = message_history.get(channel_id, [])
    return "\n".join([f"{m['author']}: {m['content']}" for m in history])

# Helper: log prompt/response for debugging
def safe_log_conversation(prompt, response):
    print("Prompt:", prompt)
    print("Response:", response)

# Helper: figure out emoji categories to respond with
def analyze_message_context(prompt, response):
    categories = []
    joined = f"{prompt} {response}".lower()
    if any(word in joined for word in ["happy", "joy", "excited"]):
        categories.append(HAPPY_EMOJIS)
    if any(word in joined for word in ["sad", "cry", "depressed"]):
        categories.append(SAD_EMOJIS)
    if any(word in joined for word in ["silly", "funny", "play"]):
        categories.append(PLAYFUL_EMOJIS)
    if any(word in joined for word in ["cool", "awesome", "epic"]):
        categories.append(COOL_EMOJIS)
    if any(word in joined for word in ["love", "heart"]):
        categories.append(LOVE_EMOJIS)
    if any(word in joined for word in ["ghost", "spooky", "halloween"]):
        categories.append(SPOOKY_EMOJIS)
    if any(word in joined for word in ["think", "why", "how"]):
        categories.append(THINKING_EMOJIS)
    if not categories:
        categories.append(MISC_EMOJIS)
    return categories

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    channel_id = message.channel.id
    if channel_id not in message_history:
        message_history[channel_id] = []
    message_history[channel_id].append({
        'author': message.author.name,
        'content': message.content
    })
    message_history[channel_id] = message_history[channel_id][-HISTORY_LENGTH:]

    if should_respond(message.content, client.user.name) or client.user in message.mentions:
        try:
            async with message.channel.typing():
                context = get_conversation_context(channel_id)
                prompt = f"Context:\n{context}\n\nCurrent message: {message.content}"
                data = {"model": model_name, "prompt": prompt, "stream": False}

                response = requests.post(ollama_url, headers={"Content-Type": "application/json"}, data=json.dumps(data))
                response.raise_for_status()
                response_text = json.loads(response.text)['response']

                safe_log_conversation(message.content, response_text)

                relevant_categories = analyze_message_context(message.content, response_text)
                num_reactions = random.randint(1, 20)
                if len(relevant_categories) < num_reactions:
                    relevant_categories *= num_reactions
                selected_emojis = [random.choice(category) for category in random.sample(relevant_categories, num_reactions)]
                for emoji in selected_emojis:
                    await message.add_reaction(emoji)

                response_with_emoji = f"{response_text} {' '.join(random.sample(selected_emojis, min(2, len(selected_emojis))))}"

                if len(response_with_emoji) > 2000:
                    thread_title = f"Response to {message.author.name}"
                    thread = await message.create_thread(name=thread_title, auto_archive_duration=60)
                    chunks = [response_with_emoji[i:i+1900] for i in range(0, len(response_with_emoji), 1900)]
                    for chunk in chunks:
                        await thread.send(chunk)
                else:
                    await message.reply(response_with_emoji, mention_author=True)

                if "sticker" in message.content.lower():
                    if message.guild and message.guild.stickers:
                        sticker = random.choice(message.guild.stickers)
                        await message.channel.send(stickers=[sticker])

        except Exception as e:
            print(f"Error: {e}")
            error_emojis = random.sample(SAD_EMOJIS + THINKING_EMOJIS, 2)
            await message.reply(f"Something went wrong! {' '.join(error_emojis)}", mention_author=True)

@client.event
async def on_reaction_add(reaction, user):
    if user != client.user:
        message_content = reaction.message.content
        relevant_categories = analyze_message_context(message_content, "")
        chosen_category = random.choice(relevant_categories)
        await reaction.message.add_reaction(random.choice(chosen_category))

client.run(TOKEN)
