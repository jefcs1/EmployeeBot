import logging
import random

import discord
from discord import app_commands
from discord.ext import commands


class EightBall(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.logger = logging.getLogger(f"EmployeeBot.{self.__class__.__name__}")
        self.bot = bot

    @commands.command(aliases=["8ball"])
    async def eightball(self, ctx):
        if ctx.author.bot:
            return

        # Respond to 8ball commands
        eightballresponses = [
            "It is certain",
            "It is decidedly so",
            "Without a doubt",
            "Yes definitely",
            "You may rely on it",
            "As I see it, yes",
            "Most likely",
            "Outlook good",
            "Yes",
            "Signs point to yes",
            "Reply hazy, try again",
            "Ask again later",
            "Better not tell you now",
            "Cannot predict now",
            "Concentrate and ask again",
            "Don't count on it",
            "My reply is no",
            "My sources say no",
            "Outlook not so good",
            "Very doubtful",
            "I'm really not sure, but send jef a free skin",
        ]

        answer = random.choice(eightballresponses)
        response = f":8ball: {answer}"
        await ctx.channel.send(response)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(EightBall(bot))
