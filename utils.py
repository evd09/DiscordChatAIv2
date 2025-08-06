import os
import random
import logging
from textblob import TextBlob

# Set up logger for helpers
logger = logging.getLogger('discord_bot')

def should_respond(msg, bot_name):
    kws = ["hey", "hello", "yo", "chat", bot_name.lower()]
    return any(k in msg.lower() for k in kws)

def get_history(message_history, ctx_id):
    hist = message_history.get(ctx_id, [])
    return "\n".join(f"{m['author']}: {m['content']}" for m in hist)

def safe_log(prompt, response):
    logger.info(f"Prompt: {prompt}\nResponse: {response}")

def sentiment_emojis(text):
    pol = TextBlob(text).sentiment.polarity
    if pol > 0.3:
        ems = ["😊","🎉","😄","💖"]
    elif pol < -0.3:
        ems = ["😞","💔","😡","😭"]
    else:
        ems = ["🤔","😐","😶","🫤"]
    return random.sample(ems, min(2, len(ems)))

def load_dynamic_prompt(prompt_file):
    dynamic_prompt = None
    if os.path.isfile(prompt_file):
        try:
            with open(prompt_file, "r", encoding="utf-8") as f:
                data = f.read().strip()
                if data:
                    dynamic_prompt = data
                    logger.info(f"Loaded saved prompt from {prompt_file}")
        except Exception as e:
            logger.warning(f"Could not load {prompt_file}: {e}")
    return dynamic_prompt
