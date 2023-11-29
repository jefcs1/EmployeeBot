import datetime
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
        if member.guild.id != 953632089339727953:
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

        difference = discord.utils.utcnow() - created_at
        years = difference.days // 365
        months = (difference.days % 365) // 30
        days = (difference.days % 365) % 30
        formatted_age = f"{years} years, {months} months, {days} days"
        leave_join = self.bot.get_channel(958327750777790465)
        j_embed = discord.Embed(
            title="",
            description=f"{member.mention} {member.display_name}",
            color=0x2ECC71,
        )
        j_embed.set_author(name="Member joined", icon_url=member.avatar)
        j_embed.set_thumbnail(url=member.avatar)
        j_embed.add_field(name="Account Age", value=formatted_age)
        j_embed.set_footer(text=f"ID: {member.id}")
        await leave_join.send(embed=j_embed)

        main_chat_channel = await self.bot.fetch_channel(953668320215830618)
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
        await main_chat_channel.send(message)

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
        welc_embed.set_footer(
            text="A little note - Triple will never DM you on discord."
        )

        await member.send(embed=welc_embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        
        TESTING = sys.platform == "darwin"
        if TESTING:
            return
        tc_id = 953632089339727953
        tc_obj = self.bot.get_guild(tc_id)
        leave_join = self.bot.get_channel(958327750777790465)
        l_embed = discord.Embed(
            title="",
            description=f"{member.mention} {member.display_name}",
            color=0xFF0000,
        )
        l_embed.set_author(name="Member Left", icon_url=member.avatar)
        l_embed.set_thumbnail(url=member.avatar)
        roles = [role.mention for role in member.roles if role != tc_obj.default_role]

        roles_per_line = 3
        roles_chunked = [
            roles[i : i + roles_per_line] for i in range(0, len(roles), roles_per_line)
        ]
        if roles_chunked:
            roles_formatted = "\n".join(
                [", ".join(role_chunk) for role_chunk in roles_chunked]
            )
        else:
            roles_formatted = "None"
        l_embed.add_field(name="Roles:", value=roles_formatted, inline=False)
        l_embed.set_footer(text=f"ID: {member.id}")
        await leave_join.send(embed=l_embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Join(bot))
