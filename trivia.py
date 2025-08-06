import discord
from discord.ext import commands
from discord import app_commands, Embed
from discord.ui import View, Button
import aiohttp
import html
import random
import re

from helpers.db import get_trivia_score, set_trivia_score, get_leaderboard

class TriviaView(View):
    def __init__(self, options, correct_label):
        super().__init__(timeout=60)
        self.correct_label = correct_label
        for label, text in options.items():
            truncated = text if len(text) <= 75 else text[:75]+"…"
            btn = Button(label=f"{label}: {truncated}", style=discord.ButtonStyle.secondary)
            async def cb(inter: discord.Interaction, choice=label):
                for c in self.children: c.disabled=True
                await inter.response.edit_message(view=self)
                msg = (f"{inter.user.mention} ✅ Correct!" if choice==self.correct_label
                       else f"{inter.user.mention} ❌ Wrong! Answer: **{self.correct_label}**")
                gid = str(inter.guild.id)
                uid = str(inter.user.id)
                correct, wrong = get_trivia_score(gid, uid)
                if choice == self.correct_label:
                    correct += 1
                else:
                    wrong += 1
                set_trivia_score(gid, uid, correct, wrong)
                await inter.followup.send(msg)
            btn.callback = cb
            self.add_item(btn)

class NsfwTriviaView(View):
    def __init__(self, options, correct_label):
        super().__init__(timeout=60)
        self.correct_label = correct_label
        for label, text in options.items():
            truncated = text if len(text)<=75 else text[:75]+"…"
            btn = Button(label=f"{label}: {truncated}", style=discord.ButtonStyle.danger)
            async def cb(inter: discord.Interaction, choice=label):
                for c in self.children: c.disabled=True
                await inter.response.edit_message(view=self)
                msg = (f"{inter.user.mention} ✅ Correct!" if choice==self.correct_label
                       else f"{inter.user.mention} ❌ Wrong! Answer: **{self.correct_label}**")
                gid = str(inter.guild.id)
                uid = str(inter.user.id)
                correct, wrong = get_trivia_score(gid, uid)
                if choice == self.correct_label:
                    correct += 1
                else:
                    wrong += 1
                set_trivia_score(gid, uid, correct, wrong)
                await inter.followup.send(msg)
            btn.callback = cb
            self.add_item(btn)

class TriviaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="trivia", description="Fetch a random multiple-choice trivia question")
    async def trivia(self, interaction: discord.Interaction):
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

    @app_commands.command(name="nsfwtrivia", description="Fetch a random NSFW trivia question (Urban Dictionary)")
    async def nsfw_trivia(self, interaction: discord.Interaction):
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

    @app_commands.command(
        name="trivialeaderboard",
        description="Show top and bottom trivia performers",
    )
    async def trivialeaderboard(self, interaction: discord.Interaction):
        leaders = get_leaderboard(str(interaction.guild.id))
        if not leaders:
            return await interaction.response.send_message("No trivia data yet.")
        stats = []
        for uid, correct, wrong in leaders:
            total = correct + wrong
            ratio = correct/total if total>0 else 0
            stats.append((uid, correct, wrong, ratio))
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

async def setup(bot):
    await bot.add_cog(TriviaCog(bot))
