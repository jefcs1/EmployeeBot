import logging
import random
import sys

import discord
from discord import app_commands
from discord.ext import commands


class Join(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.logger = logging.getLogger(f"EmployeeBot.{self.__class__.__name__}")
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        TESTING = sys.platform == "darwin"
        if TESTING:
            return

        created_at = member.created_at

        tc_id = 953632089339727953
        tc_obj = self.bot.get_guild(tc_id)

        age_in_minutes = (discord.utils.utcnow() - created_at).total_seconds() / 60

        if age_in_minutes < 30:
            await member.kick()
            mod_logs_channel_id = 958328194027638817
            mod_logs_channel = self.bot.get_channel(mod_logs_channel_id)
            embed = discord.Embed(
                title="New Account Kicked!",
                description=f"I kicked {member.mention}, because their account was less than 30 minutes old.",
                color=0xFF0000,
            )
            await mod_logs_channel.send(embed=embed)
            return

        main_chat_channel = await self.bot.fetch_channel(953668320215830618)
        joins_channel = await self.bot.fetch_channel(1148259530375958618)
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
        await joins_channel.send(message)

        welc_embed = discord.Embed(
            title="Welcome to Traders Compound!",
            description="Our aim is to provide a toxicity-free community for Traders and skin-lovers alike!\nWe hope you enjoy your time with us!",
            color=0x86DEF2,
        )
        welc_embed.set_author(name="Traders Compound", icon_url=tc_obj.icon.url)
        welc_embed.add_field(
            name="SkinFlow, instant Cash-Out for your skins.",
            value="Traders Compound is currently partnered with SkinFlow. SkinFlow is an instant Cashout website, with the best rates in the market.\n[Cash Out your Skins with a 2% bonus with This Link](https://skinflow.gg/?referral=TC)",
        )
        welc_embed.set_footer(text="A little note - Triple will never DM you on discord.")


        await member.send(embed=welc_embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Join(bot))
