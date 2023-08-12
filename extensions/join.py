import logging
import random

import discord
from discord import app_commands
from discord.ext import commands


class Join(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.logger = logging.getLogger(f"EmployeeBot.{self.__class__.__name__}")
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = await self.bot.fetch_channel(953668320215830618)
        welcome_messages = [
            f"Everyone welcome {member.mention} to Traders Compound! <:3WelcomeHeart:1106629900451971226>",
            f"Good to have you {member.mention}! <:HeartTC:1102665571872555099>",
            f"Hi {member.mention}, welcome to the server! <:3Howdy:1106529942067486750>",
            f"{member.mention} just showed up, make them feel welcome! <:Heart:1106339040472596500>",
            f"Say hello to our newest member, {member.mention}! <:Hi:1106344235973759016>",
            f"Welcome {member.mention}, we hope you brought pizza! <:DogCheemsSatisfied:1108733939239108698>",
            f"Welcome to our community {member.mention}! <a:1TCSKELETONSPIN:1101450995776622662>",
        ]
        message = random.choice(welcome_messages)
        await channel.send(message)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Join(bot))
