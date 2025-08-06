import discord
from discord.ext import commands
from discord import app_commands
from helpers.db import set_persona, get_persona
from helpers.personalities import PERSONALITIES, NSFW_ONLY_PERSONAS

def character_embed(persona, info_msg=None):
    desc = PERSONALITIES.get(persona, "")
    embed = discord.Embed(
        title=f"Your Current Persona: {persona}",
        description=desc,
        color=discord.Color.blue()
    )
    if info_msg:
        embed.add_field(name="Status", value=info_msg, inline=False)
    return embed

class CharacterSelect(discord.ui.Select):
    def __init__(self, current_persona, allowed_personas):
        options = [
            discord.SelectOption(
                label=persona,
                description=PERSONALITIES[persona][:90],
                default=(persona == current_persona)
            )
            for persona in allowed_personas
        ]
        super().__init__(
            placeholder="Choose a persona...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        new_persona = self.values[0]
        set_persona(str(interaction.guild.id), str(interaction.user.id), new_persona)
        info_msg = f"✅ Persona set to **{new_persona}**!"
        try:
            await interaction.response.edit_message(
                embed=character_embed(new_persona, info_msg),
                view=CharacterView(interaction, new_persona)
            )
        except discord.NotFound:
            await interaction.followup.send(
                "Sorry, this menu expired. Please run /character again.",
                ephemeral=True
            )

class CharacterView(discord.ui.View):
    def __init__(self, interaction, current_persona):
        super().__init__(timeout=120)
        self.interaction = interaction
        self.current_persona = current_persona

        allowed = [k for k in PERSONALITIES.keys() if k not in NSFW_ONLY_PERSONAS or interaction.channel.is_nsfw()]
        self.add_item(CharacterSelect(current_persona, allowed))

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.interaction.user.id:
            await interaction.response.send_message("You can't control someone else's persona UI!", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Reset to Default", style=discord.ButtonStyle.danger)
    async def reset_character(self, interaction: discord.Interaction, button: discord.ui.Button):
        set_persona(str(interaction.guild.id), str(interaction.user.id), "friendly")
        info_msg = "✅ Persona reset to **friendly**!"
        try:
            await interaction.response.edit_message(
                embed=character_embed("friendly", info_msg),
                view=CharacterView(interaction, "friendly")
            )
        except discord.NotFound:
            await interaction.followup.send(
                "Sorry, this menu expired. Please run /character again.",
                ephemeral=True
            )

class CharacterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="character", description="Change, reset, or view your AI character/persona")
    async def character(self, interaction: discord.Interaction):
        current = get_persona(str(interaction.guild.id), str(interaction.user.id))
        view = CharacterView(interaction, current)
        await interaction.response.send_message(
            embed=character_embed(current, "Use the dropdown to select a persona, or the button to reset."),
            view=view,
            ephemeral=True  
        )

async def setup(bot):
    await bot.add_cog(CharacterCog(bot))
