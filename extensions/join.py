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

        created_at = member.created_at
        print(f"Created at: {created_at}")

        age_in_hours = (discord.utils.utcnow() - created_at).total_seconds() / 3600
        print(f"Age in hours: {age_in_hours}")

        if age_in_hours < 1:
            await member.kick()

        mod_logs_channel_id = 958328194027638817
        mod_logs_channel = self.bot.get_channel(mod_logs_channel_id)

        embed = discord.Embed(title = "New Account Kicked!", description=f"I kicked {member.mention}, because their account was less than 1 hour old.")

        await mod_logs_channel.send(embed=embed)

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
