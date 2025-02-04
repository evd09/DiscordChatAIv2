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

TOKEN = os.getenv('DISCORD_TOKEN')
print(f"Token loaded: {'Found token' if TOKEN else 'No token found'}")

# Initialize Discord bot with more intents
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
client = discord.Client(intents=intents)

# Ollama API configuration
ollama_url = "http://localhost:11434/api/generate"
model_name = "hermes3"

# Emoji collections
HAPPY_EMOJIS = ['😊', '😄', '😃', '🥰', '😘', '😋', '😍', '🤗', '🌟', '✨', '💫', '⭐']
SAD_EMOJIS = ['😢', '😭', '🥺', '😔', '😪', '💔', '😿', '🫂', '🥀']
PLAYFUL_EMOJIS = ['😜', '🤪', '😝', '😋', '🤭', '🙈', '🙉', '🙊', '🐱', '🐰', '🦊', '🐼']
COOL_EMOJIS = ['😎', '🕶️', '🔥', '💯', '🆒', '🤙', '👑', '💪', '✌️', '🎮', '🎯', '🎪']
LOVE_EMOJIS = ['❤️', '🧡', '💛', '💚', '💙', '💜', '🤍', '🖤', '💝', '💖', '💗', '💓']
SPOOKY_EMOJIS = ['💀', '👻', '🎃', '🦇', '🕷️', '🕸️', '🧟‍♂️', '🧟‍♀️', '👺', '👹', '😈', '🤡']
THINKING_EMOJIS = ['🤔', '🧐', '💭', '💡', '🎯', '📚', '🔍', '💻', '📝']
MISC_EMOJIS = ['🌈', '🎨', '🎭', '🎪', '🎡', '🎢', '🎠', '🌸', '🌺', '🌷', '🌹', '🍀']


# Message history storage (you might want to use a proper database in production)
message_history = {}  # {channel_id: [last_n_messages]}
HISTORY_LENGTH = 10  # Number of messages to keep in history

def should_respond(message_content, bot_name):
    """
    Determine if the bot should respond to a message
    """ 
    # Convert both to lowercase for case-insensitive matching
    content_lower = message_content.lower()
    bot_name_lower = bot_name.lower()

    # Direct mention check (already handled in main function)
    if f"<@{client.user.id}>" in message_content:
        return True
    
    # Check if the bot's name is mentioned
    if bot_name_lower in content_lower:
        return True
    
    # Check for question patterns
    question_patterns = [
        r'\?$',  # Ends with question mark
        r'^(what|who|where|when|why|how|can|could|would|should|is|are|do|does|did)',  # Starts with question word
    ]
    
    for pattern in question_patterns:
        if re.search(pattern, content_lower):
            return random.random() < 0.5  # 50% chance to respond to questions
    
    # Random chance to respond to messages (10%)
    return random.random() < 0.1

def analyze_message_context(message_content, response_text):
    """Analyze message context to determine appropriate emoji categories"""
    content = message_content.lower() + " " + response_text.lower()
    
    relevant_categories = []
    
    # Check for different emotional contexts
    if any(word in content for word in ['happy', 'great', 'awesome', 'wonderful', 'yay', 'good']):
        relevant_categories.append(HAPPY_EMOJIS)
    
    if any(word in content for word in ['sad', 'sorry', 'unfortunate', 'bad', 'wrong', 'error']):
        relevant_categories.append(SAD_EMOJIS)
    
    if any(word in content for word in ['love', 'heart', 'care', 'sweet', 'cute']):
        relevant_categories.append(LOVE_EMOJIS)
    
    if any(word in content for word in ['think', 'question', 'how', 'what', 'why', 'learn', 'study']):
        relevant_categories.append(THINKING_EMOJIS)
    
    if any(word in content for word in ['fun', 'play', 'game', 'lol', 'haha', 'joke']):
        relevant_categories.append(PLAYFUL_EMOJIS)
    
    if any(word in content for word in ['cool', 'awesome', 'nice', 'amazing', 'wow']):
        relevant_categories.append(COOL_EMOJIS)
    
    if any(word in content for word in ['spooky', 'scary', 'halloween', 'ghost', 'dead', 'monster']):
        relevant_categories.append(SPOOKY_EMOJIS)

    # If no relevant categories found, use a default set
    
    if not relevant_categories:
        relevant_categories = [HAPPY_EMOJIS, MISC_EMOJIS, PLAYFUL_EMOJIS]
    
    return relevant_categories


def get_conversation_context(channel_id):
    """Get the recent conversation context from the channel"""
    if channel_id in message_history:
        return "\n".join([f"{msg['author']}: {msg['content']}" for msg in message_history[channel_id]])
    return ""


def safe_log_conversation(user_message, bot_response):
    """Safely log conversation with proper encoding handling"""
    try:
        with open('conversations.log', 'a', encoding='utf-8') as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}]\nUser: {user_message}\nBot: {bot_response}\n\n")
    except Exception as e:
        print(f"Logging error: {e}")

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Update message history
    channel_id = message.channel.id
    if channel_id not in message_history:
        message_history[channel_id] = []
    
    message_history[channel_id].append({
        'author': message.author.name,
        'content': message.content
    })
    
    # Keep only the last N messages
    message_history[channel_id] = message_history[channel_id][-HISTORY_LENGTH:]

    # Check if the bot should respond
    if should_respond(message.content, client.user.name) or client.user in message.mentions:
        try:
            # Show typing indicator
            async with message.channel.typing():
            # Get conversation context
                context = get_conversation_context(channel_id)
            
            # Prepare prompt with context
            prompt = f"Context:\n{context}\n\nCurrent messAage: {message.content}"
            
                # Generate response using Ollama API
            data = {
                "model": model_name,
                "prompt": prompt,
                "stream": False
            }
            response = requests.post(ollama_url, headers={"Content-Type": "application/json"}, data=json.dumps(data))
            response.raise_for_status()
            
            response_text = json.loads(response.text)['response']
            
            # Log the conversation with safe encoding handling
            safe_log_conversation(message.content, response_text)

            # Get contextually appropriate emoji categories
            relevant_categories = analyze_message_context(message.content, response_text)
            
            # Randomly select number of emojis (1-20)
            num_reactions = random.randint(1, 20) # Random number of reactions, this is chaotic
            
            # If we have fewer categories than desired reactions, we can reuse categories
            if len(relevant_categories) < num_reactions:
                relevant_categories = relevant_categories * num_reactions
            
            # Select random emojis from relevant categories
            selected_emojis = [random.choice(category) for category in random.sample(relevant_categories, num_reactions)]
            
            # Add reactions
            for emoji in selected_emojis:
                await message.add_reaction(emoji)
            
            # Add random emojis to the response text
            response_with_emoji = f"{response_text} {' '.join(random.sample(selected_emojis, min(2, len(selected_emojis))))}"
            await message.reply(response_with_emoji, mention_author=True)

            # Handle sticker requests
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