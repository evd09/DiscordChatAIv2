import os
import discord
from discord.ext import commands
import aiohttp
import random
import emoji
import json
from dotenv import load_dotenv

from helpers.db import get_persona
from helpers.utils import (
    should_respond, get_history, safe_log, sentiment_emojis
)
from helpers.personalities import PERSONALITIES, NSFW_ONLY_PERSONAS

# ─── Logging ───────────────────────────────────────────────────────────
os.makedirs("logs", exist_ok=True)
import logging
from logging.handlers import RotatingFileHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        RotatingFileHandler("logs/bot.log", maxBytes=2_000_000, backupCount=5, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('discord_bot')

# ─── Setup & Config ───────────────────────────────────────────────────────────
load_dotenv()
TOKEN        = os.getenv('DISCORD_TOKEN')
OLLAMA_URL   = os.getenv('OLLAMA_URL', 'http://localhost:11434/api/generate')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'hermes3')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ─── Globals ───────────────────────────────────────────────────────────────────
ALL_EMOJIS      = [e for e in emoji.EMOJI_DATA.keys() if len(e) <= 2]
message_history = {}
HISTORY_LENGTH  = 10

# ─── Events ───────────────────────────────────────────────────────────────────
@bot.event
async def on_ready():
    logger.info(f'✅ Logged in as {bot.user}')
    try:
        await bot.tree.sync()
        logger.info("Synced all commands globally.")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.author == bot.user:
        return
    cid = message.channel.id
    message_history.setdefault(cid, []).append({
        'author': message.author.name,
        'content': message.content
    })
    message_history[cid] = message_history[cid][-HISTORY_LENGTH:]
    if message.guild:  # Only respond in guild channels, not DMs
        persona = get_persona(str(message.guild.id), str(message.author.id))
    else:
        persona = "friendly"
    persona_prompt = PERSONALITIES.get(persona, "")
    history_text = get_history(message_history, cid)
    final_prompt = (
        f"{persona_prompt}\n\nContext:\n{history_text}\n\nCurrent message: {message.content}"
    )
    if should_respond(message.content, bot.user.name) or bot.user in message.mentions:
        try:
            async with message.channel.typing():
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        OLLAMA_URL,
                        headers={"Content-Type":"application/json"},
                        data=json.dumps({"model": OLLAMA_MODEL, "prompt": final_prompt, "stream": False})
                    ) as resp:
                        result = await resp.json()
                reply = result.get('response','')
                safe_log(final_prompt, reply)
                emojis = sentiment_emojis(reply)
                for e in emojis:
                    try: await message.add_reaction(e)
                    except: pass
                out = f"{reply} {' '.join(emojis)}"
                if len(out) > 2000:
                    thread = await message.create_thread(name=f"Response to {message.author.name}", auto_archive_duration=60)
                    for i in range(0, len(out), 1900): await thread.send(out[i:i+1900])
                else:
                    await message.reply(out, mention_author=True)
        except Exception as err:
            logger.error(f"on_message error: {err}")
            await message.reply("Something went wrong! 🤖", mention_author=True)

# ─── Slash Commands ────────────────────────────────────────────────────────────

@bot.tree.command(name="help", description="Show available commands")
async def help_command(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)  # Acknowledge right away
    sfw_personas = [k for k in PERSONALITIES.keys() if k not in NSFW_ONLY_PERSONAS]
    nsfw_personas = NSFW_ONLY_PERSONAS
    text = (
        "**AI Character/Persona**\n"
        "• /character (set, view, or reset your AI style)\n"
        f"SFW: {', '.join(sfw_personas)}\n"
        f"NSFW-only: {', '.join(nsfw_personas)}\n"
        "_NSFW-only personas can only be set in NSFW channels._\n\n"
        "**Mini-Games**\n"
        "• /8ball <question>\n"
        "• /trivia\n"
        "• /nsfwtrivia (NSFW only)\n"
        "• /trivialeaderboard"
    )
    await interaction.followup.send(text, ephemeral=True)

# ─── Load Cogs ────────────────────────────────────────────────────────────────

import asyncio

async def main():
    await bot.load_extension("cogs.character")  # loads your interactive character UI
    await bot.load_extension("cogs.trivia")     # loads trivial commands
    await bot.load_extension("cogs.fun")     # loads fun & 8ball commands
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
