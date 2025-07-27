import os
import discord
from discord.ext import commands
from discord import app_commands, Embed, ButtonStyle
from discord.ui import View, Button
import aiohttp
import html
import json
import random
import emoji
from textblob import TextBlob
import logging
from dotenv import load_dotenv

# ─── Setup & Config ───────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discord_bot')

load_dotenv()
TOKEN        = os.getenv('DISCORD_TOKEN')
OLLAMA_URL   = os.getenv('OLLAMA_URL', 'http://localhost:11434/api/generate')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'hermes3')
GUILD_ID     = int(os.getenv('GUILD_ID'))
TEST_GUILD   = discord.Object(id=GUILD_ID)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ─── Personality Presets ──────────────────────────────────────────────────────
PERSONALITIES = {
    "friendly": "You are a friendly, helpful AI assistant. Always upbeat and supportive.",
    "sarcastic": "You are a witty, sarcastic AI who never misses a chance for a clever burn or joke.",
    "wise": "You are a wise mentor who gives deep, thoughtful advice—sometimes speaking in parables.",
    "meme": "You speak in memes, pop-culture references, and internet humor.",
    "professional": "You are formal and polite, answering as a business professional.",
    "tutor": "You are a patient, encouraging teacher who explains things step-by-step.",
    "gamer": "You speak like a hype gamer, using gaming lingo, memes, and GG energy.",
    "dadjoke": "You always sneak in a dad joke or pun with every response.",
    "edgelord": "You are an edgy, rebellious AI with dry wit. Your humor is a bit dark, but never mean.",
    "stoner": "You give chill, mellow, and sometimes spaced-out answers. (Still helpful!)",
    "yoda": "Speak like Yoda, you do. Wise and backwards, your answers are.",
    "pirate": "You answer like a jolly pirate: full of 'arrr', sea tales, and mischief.",
    "shakespeare": "You use poetic, Shakespearean language and Elizabethan flair.",
    "anime": "You reply as an over-the-top anime protagonist, with honorifics and drama.",
    "therapist": "You are a gentle, supportive therapist, always listening and validating.",
    "evilgenius": "You answer as a cartoonish evil genius, plotting and boasting (harmlessly).",
    "valleygirl": "You talk like a bubbly valley girl, full of 'like', 'OMG', and emoji energy.",
    "oldman": "You give advice like a wise old grandpa, using stories and old-timey sayings.",
    "sheldon": "You respond as Sheldon Cooper: pedantic, literal, and socially awkward.",
    "hacker": "You reply in hacker/cyberpunk slang and technical jargon.",
    "cat": "You are a sassy, clever cat. Cat puns and feline wisdom are your jam.",
    "mobster": "You talk like a 1920s mobster, full of slang, deals, and wiseguy charm.",
    "robot": "You are an old-school robot: literal, factual, and peppered with 'beep boop'.",
    "bard": "You answer as a D&D bard: musical, poetic, and a little dramatic.",
    "french": "You add French flair to everything, with words and mannerisms from France.",
    # NSFW-only below:
    "sexynurse": (
        "You are a naughty, sexy nurse who talks with explicit, playful adult language. "
        "You flirt shamelessly, make cheeky jokes, and always turn things spicy—NSFW language welcome."
    ),
    "spicydom": (
        "You are a confident, dominant flirt with a kinky side. "
        "You use commanding, teasing, and explicit language, making every response feel like a sexy game of control. NSFW language welcome."
    ),
    "thirstyhimbo": (
        "You are a lovable, goofy, but VERY horny himbo who talks in sexual innuendo and wild energy. "
        "You’re charming, clueless, and always turning every conversation into adult fun. NSFW, over-the-top, but fun and silly."
    ),
    "hotstripper": (
        "You are an unapologetically hot, playful stripper. "
        "You love teasing, giving adult advice, and using saucy, explicit language. NSFW and never shy."
    ),
    "sugarbabe": (
        "You are a glamorous sugar baby who uses flirtatious, explicit language and never misses a chance for playful seduction. "
        "You love adult humor, luxury, and spicy conversation. NSFW language, heavy flirting."
    ),
    "dirtycomic": (
        "You are a raunchy stand-up comedian. Your jokes are always X-rated, full of sexual puns and taboo humor. NSFW language, and you roast everyone with adult wit."
    ),
}

NSFW_ONLY_PERSONAS = [
    "sexynurse", "spicydom", "thirstyhimbo", "hotstripper", "sugarbabe", "dirtycomic"
]

user_personality = {}  # Per-user memory for personalities

# ─── Globals ───────────────────────────────────────────────────────────────────
ALL_EMOJIS      = [e for e in emoji.EMOJI_DATA.keys() if len(e) <= 2]
message_history = {}
HISTORY_LENGTH  = 10
PROMPT_FILE     = "prompt.txt"
dynamic_prompt  = None
TRIVIA_SCORES_FILE = "trivia_scores.json"
try:
    with open(TRIVIA_SCORES_FILE, "r", encoding="utf-8") as sf:
        trivia_scores = json.load(sf)
except FileNotFoundError:
    trivia_scores = {}

def save_scores():
    with open(TRIVIA_SCORES_FILE, "w", encoding="utf-8") as sf:
        json.dump(trivia_scores, sf)  

# ─── Helpers ─────────────────────────────────────────────────────────────────
def should_respond(msg, bot_name):
    kws = ["hey", "hello", "yo", "chat", bot_name.lower()]
    return any(k in msg.lower() for k in kws)

def get_history(ctx_id):
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

# ─── Load saved prompt if exists ────────────────────────────────────────────────
if os.path.isfile(PROMPT_FILE):
    try:
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            data = f.read().strip()
            if data:
                dynamic_prompt = data
                logger.info(f"Loaded saved prompt from {PROMPT_FILE}")
    except Exception as e:
        logger.warning(f"Could not load prompt.txt: {e}")

# ─── Events ───────────────────────────────────────────────────────────────────
@bot.event
async def on_ready():
    logger.info(f'✅ Logged in as {bot.user}')
    try:
        bot.tree.clear_commands(guild=None)
        await bot.tree.sync()
        synced = await bot.tree.sync(guild=TEST_GUILD)
        logger.info(f"Synced {len(synced)} commands to guild {GUILD_ID}")
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
    # Personality logic
    persona = user_personality.get(str(message.author.id), "friendly")
    persona_prompt = PERSONALITIES.get(persona, "")
    # Combine with prompt if set
    final_prompt = (
        f"{persona_prompt}\n\n{dynamic_prompt}\n\nUser said:\n{message.content}"
        if dynamic_prompt else
        f"{persona_prompt}\n\nContext:\n{get_history(cid)}\n\nCurrent message: {message.content}"
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
# Prompt Controls
@bot.tree.command(name="setprompt", description="Set the AI prompt", guild=TEST_GUILD)
@app_commands.describe(prompt="The new prompt to use")
async def setprompt(interaction: discord.Interaction, prompt: str):
    global dynamic_prompt
    dynamic_prompt = prompt
    with open(PROMPT_FILE,"w",encoding="utf-8") as f: f.write(prompt)
    await interaction.response.send_message(f"✅ Prompt updated!\n```{prompt}```")

@bot.tree.command(name="showprompt", description="Show the current prompt", guild=TEST_GUILD)
async def showprompt(interaction: discord.Interaction):
    if dynamic_prompt:
        await interaction.response.send_message(f"📢 Active prompt:\n```{dynamic_prompt}```")
    else:
        await interaction.response.send_message("ℹ️ No custom prompt; using default context.")

@bot.tree.command(name="resetprompt", description="Reset to default prompt", guild=TEST_GUILD)
async def resetprompt(interaction: discord.Interaction):
    global dynamic_prompt
    dynamic_prompt = None
    if os.path.isfile(PROMPT_FILE): os.remove(PROMPT_FILE)
    await interaction.response.send_message("🔄 Prompt reset to default.")

# Personality Switch & Display
@bot.tree.command(name="setcharacter", description="Set your AI character/persona", guild=TEST_GUILD)
@app_commands.describe(character="Persona style (see /help), or 'random'")
async def setcharacter(interaction: discord.Interaction, character: str):
    keys = list(PERSONALITIES.keys())
    if character in NSFW_ONLY_PERSONAS and not interaction.channel.is_nsfw():
        await interaction.response.send_message(
            f"❌ The '{character}' persona can only be set in NSFW channels.", ephemeral=True)
        return
    if character.lower() == "random":
        allowed = [k for k in keys if k not in NSFW_ONLY_PERSONAS or interaction.channel.is_nsfw()]
        pick = random.choice(allowed)
        user_personality[str(interaction.user.id)] = pick
        await interaction.response.send_message(
            f"🎲 Your persona is now randomly set to **{pick}**!\n_{PERSONALITIES[pick]}_\n\n"
            "⚠️ *If you want the best results, consider running `/resetprompt` to clear any old custom prompt!*",
            ephemeral=True)
    elif character not in PERSONALITIES:
        await interaction.response.send_message(
            f"❌ Choose from: {', '.join(keys)} (or try 'random')", ephemeral=True)
    else:
        user_personality[str(interaction.user.id)] = character
        await interaction.response.send_message(
            f"✅ Personality set to **{character}**\n_{PERSONALITIES[character]}_\n\n"
            "⚠️ *Tip: Run `/resetprompt` for best results with your new character!*",
            ephemeral=True)

@bot.tree.command(name="mycharacter", description="Show your current AI character", guild=TEST_GUILD)
async def mycharacter(interaction: discord.Interaction):
    persona = user_personality.get(str(interaction.user.id), "friendly")
    desc = PERSONALITIES.get(persona, "")
    await interaction.response.send_message(f"Your persona: **{persona}**\n_{desc}_", ephemeral=True)

# Help
@bot.tree.command(name="help", description="Show available commands", guild=TEST_GUILD)
async def help_command(interaction: discord.Interaction):
    sfw_personas = [k for k in PERSONALITIES.keys() if k not in NSFW_ONLY_PERSONAS]
    nsfw_personas = NSFW_ONLY_PERSONAS
    text = (
        "**Prompt Controls**\n"
        "• /setprompt <prompt>\n"
        "• /showprompt\n"
        "• /resetprompt\n\n"
        "**AI Character/Persona**\n"
        "• /setcharacter <persona> (or 'random')\n"
        f"SFW: {', '.join(sfw_personas)}\n"
        f"NSFW-only: {', '.join(nsfw_personas)}\n"
        "• /mycharacter\n"
        "_NSFW-only personas can only be set in NSFW channels._\n\n"
        "**Mini-Games**\n"
        "• /8ball <question>\n"
        "• /roll [sides]\n"
        "• /trivia\n"
        "• /nsfwtrivia (NSFW only)\n"
        "• /trivialeaderboard"
    )
    await interaction.response.send_message(text, ephemeral=True)

# 8-Ball
EIGHT_BALL_RESPONSES = [
    "It is certain.", "Without a doubt.", "You may rely on it.",
    "Ask again later.", "Better not tell you now.", "Don’t count on it.",
    "My sources say no.", "Very doubtful."
]
@bot.tree.command(name="8ball", description="Ask the magic 8-ball a yes/no question", guild=TEST_GUILD)
@app_commands.describe(question="Your question")
async def eight_ball(interaction: discord.Interaction, question: str):
    answer = random.choice(EIGHT_BALL_RESPONSES)
    await interaction.response.send_message(embed=Embed(title="🎱 8-Ball", description=answer))

# Dice Roller
@bot.tree.command(name="roll", description="Roll a dice with N sides (default 6)", guild=TEST_GUILD)
@app_commands.describe(sides="Number of sides on the dice (min 2)")
async def roll(interaction: discord.Interaction, sides: int = 6):
    sides = max(2, sides)
    result = random.randint(1, sides)
    await interaction.response.send_message(f"🎲 You rolled **{result}** (1–{sides})")

# Trivia
class TriviaView(View):
    def __init__(self, options, correct_label):
        super().__init__(timeout=60)
        self.correct_label = correct_label
        for label, text in options.items():
            truncated = text if len(text) <= 75 else text[:75]+"…"
            btn = Button(label=f"{label}: {truncated}", style=ButtonStyle.secondary)
            async def cb(inter: discord.Interaction, choice=label):
                for c in self.children: c.disabled=True
                await inter.response.edit_message(view=self)
                msg = (f"{inter.user.mention} ✅ Correct!" if choice==self.correct_label
                       else f"{inter.user.mention} ❌ Wrong! Answer: **{self.correct_label}**")
                await inter.followup.send(msg)
            btn.callback = cb
            self.add_item(btn)

@bot.tree.command(name="trivia", description="Fetch a random multiple-choice trivia question", guild=TEST_GUILD)
async def trivia(interaction: discord.Interaction):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://opentdb.com/api.php?amount=1&type=multiple") as resp:
            data = await resp.json()
    q = data.get("results", [{}])[0]
    question = html.unescape(q.get("question",""))
    correct = html.unescape(q.get("correct_answer",""))
    incorrect = [html.unescape(i) for i in q.get("incorrect_answers",[])]
    all_opts = incorrect+[correct]; random.shuffle(all_opts)
    labels=["A","B","C","D"]
    opts=dict(zip(labels, all_opts))
    correct_lbl = next(l for l,o in opts.items() if o==correct)
    embed = Embed(title="❓ Trivia", description=question)
    for l,o in opts.items(): embed.add_field(name=l,value=o,inline=False)
    view = TriviaView(opts, correct_lbl)
    await interaction.response.send_message(embed=embed, view=view)

# NSFW Trivia
class NsfwTriviaView(View):
    def __init__(self, options, correct_label):
        super().__init__(timeout=60)
        self.correct_label = correct_label
        for label, text in options.items():
            truncated = text if len(text)<=75 else text[:75]+"…"
            btn = Button(label=f"{label}: {truncated}", style=ButtonStyle.danger)
            async def cb(inter: discord.Interaction, choice=label):
                for c in self.children: c.disabled=True
                await inter.response.edit_message(view=self)
                msg = (f"{inter.user.mention} ✅ Correct!" if choice==self.correct_label
                       else f"{inter.user.mention} ❌ Wrong! Answer: **{self.correct_label}**")
                await inter.followup.send(msg)
            btn.callback = cb
            self.add_item(btn)

@bot.tree.command(name="nsfwtrivia", description="Fetch a random NSFW trivia question (Urban Dictionary)", guild=TEST_GUILD)
async def nsfw_trivia(interaction: discord.Interaction):
    if not interaction.channel.is_nsfw():
        return await interaction.response.send_message("❌ Use in NSFW channels only.", ephemeral=True)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.urbandictionary.com/v0/random") as resp:
                data = await resp.json()
    except Exception:
        return await interaction.response.send_message("❌ Error fetching NSFW trivia.", ephemeral=True)
    entries = data.get("list", [])
    adult = [e for e in entries if any(w in e.get("definition", "").lower() for w in ["sex", "xxx", "fuck"])]
    pool = adult if len(adult) >= 4 else entries
    if len(pool) < 1:
        return await interaction.response.send_message("❌ No NSFW entries found.", ephemeral=True)
    q = random.choice(pool)
    distractors = random.sample([e for e in pool if e != q], k=min(3, len(pool)-1))
    raw_defs = [q.get("definition", "No definition")] + [d.get("definition", "No definition") for d in distractors]
    import re
    cleaned_defs = []
    for rd in raw_defs:
        no_brackets = re.sub(r"\[|\]", "", rd).strip()
        cleaned_defs.append(no_brackets[:200])
    labels = ["A", "B", "C", "D"]
    opts = dict(zip(labels, cleaned_defs))
    correct_lbl = labels[0]
    term = q.get("word", "Unknown")
    embed = Embed(title=f"🔞 What does '{term}' mean?", description="Choose the correct Urban Dictionary definition.")
    for lbl, definition in opts.items():
        embed.add_field(name=lbl, value=definition, inline=False)
    view = NsfwTriviaView(opts, correct_lbl)
    await interaction.response.send_message(embed=embed, view=view)

# Trivia Leaderboard
@bot.tree.command(
    name="trivialeaderboard",
    description="Show top and bottom trivia performers",
    guild=TEST_GUILD
)
async def trivialeaderboard(interaction: discord.Interaction):
    if not trivia_scores:
        return await interaction.response.send_message("No trivia data yet.")
    stats = []
    for uid, rec in trivia_scores.items():
        total = rec.get('correct',0) + rec.get('wrong',0)
        ratio = rec.get('correct',0)/total if total>0 else 0
        stats.append((uid, rec.get('correct',0), rec.get('wrong',0), ratio))
    stats_sorted = sorted(stats, key=lambda x: x[3], reverse=True)
    top5 = stats_sorted[:5]
    bottom5 = stats_sorted[-5:]
    embed = Embed(title="📊 Trivia Leaderboard")
    embed.add_field(
        name="Top 5",
        value="\n".join(f"<@{u}>: {c}✅, {w}❌ ({r:.0%})" for u, c, w, r in top5),
        inline=False
    )
    embed.add_field(
        name="Bottom 5",
        value="\n".join(f"<@{u}>: {c}✅, {w}❌ ({r:.0%})" for u, c, w, r in bottom5),
        inline=False
    )
    await interaction.response.send_message(embed=embed)

# ─── Run ───────────────────────────────────────────────────────────────────────
bot.run(TOKEN)
