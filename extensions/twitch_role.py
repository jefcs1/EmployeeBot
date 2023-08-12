import logging

import discord  # type: ignore
from discord import app_commands
from discord.ext import commands


class TwitchRole(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.logger = logging.getLogger(f"EmployeeBot.{self.__class__.__name__}")
        self.bot = bot

    live_role_id = 1122209929659428916
    premium_role_id = 1121860722054414397

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        guild = after.guild
        live_role = guild.get_role(self.live_role_id)
        premium_role = guild.get_role(self.premium_role_id)

        if premium_role not in after.roles:
            return

        if not live_role:
            return

        if after.activity and isinstance(after.activity, discord.Streaming):
            if live_role not in after.roles:
                await after.add_roles(live_role)
        else:
            if live_role in after.roles:
                await after.remove_roles(live_role)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TwitchRole(bot))
