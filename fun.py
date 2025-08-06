import discord
from discord.ext import commands
from discord import app_commands, Embed
import aiohttp
import random

EIGHT_BALL_RESPONSES = [
    "It is certain.", "Without a doubt.", "You may rely on it.",
    "Ask again later.", "Better not tell you now.", "Don’t count on it.",
    "My sources say no.", "Very doubtful."
]

class FunCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="fortune", description="Receive a random fortune!")
    async def fortune(self, interaction: discord.Interaction):
        fortune = None
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get("https://yerkee.com/api/fortune") as resp:
                    data = await resp.json()
                fortune = data.get("fortune")
            except Exception:
                pass
        if not fortune:
            fallback_fortunes = [
                "Adventure awaits you at every corner.",
                "You will soon receive a pleasant surprise.",
                "A good deed will bring you unexpected rewards.",
                "Fortune favors the bold.",
                "Your hard work will soon pay off."
            ]
            fortune = random.choice(fallback_fortunes)
        await interaction.response.send_message(
            embed=Embed(title="🍪 Your Fortune", description=fortune)
        )

    @app_commands.command(name="roast", description="Get a roast, or roast someone else!")
    @app_commands.describe(user="User to roast (optional, defaults to yourself)")
    async def roast(self, interaction: discord.Interaction, user: discord.User = None):
        if user is None:
            user = interaction.user
        roast = None
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get("https://evilinsult.com/generate_insult.php?lang=en&type=json") as resp:
                    data = await resp.json()
                roast = data.get("insult")
            except Exception:
                pass
        if not roast:
            fallback_roasts = [
                f"{user.display_name}, you're as sharp as a marble.",
                f"{user.display_name}, you bring everyone so much joy when you leave the room.",
                f"{user.display_name}, I'd agree with you but then we'd both be wrong.",
                f"{user.display_name}, you're proof that evolution can go in reverse.",
                f"{user.display_name}, your secrets are always safe with me. I never listen to them anyway."
            ]
            roast = random.choice(fallback_roasts)
        await interaction.response.send_message(
            embed=Embed(title="🔥 Roast", description=roast)
        )

    @app_commands.command(name="8ball", description="Ask the magic 8-ball a yes/no question")
    @app_commands.describe(question="Your question")
    async def eight_ball(self, interaction: discord.Interaction, question: str):
        answer = random.choice(EIGHT_BALL_RESPONSES)
        await interaction.response.send_message(embed=Embed(title="🎱 8-Ball", description=answer))

async def setup(bot):
    await bot.add_cog(FunCog(bot))
