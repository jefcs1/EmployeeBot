import logging

import discord  # type: ignore
from discord import app_commands
from discord.ext import commands


class TwitchRole(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.logger = logging.getLogger(f"EmployeeBot.{self.__class__.__name__}")
        self.bot = bot

    live_role_id = 1122209929659428916
    classified_role_id = 1121931624670580908
    covert_role_id = 1121860931861893190
    contraband_role_id = 1121860948370673747

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        guild = after.guild
        live_role = guild.get_role(self.live_role_id)
        classified_role = guild.get_role(self.classified_role_id)
        covert_role = guild.get_role(self.covert_role_id)
        contraband_role = guild.get_role(self.contraband_role_id)

        if (
            classified_role not in after.roles
            and covert_role not in after.roles
            and contraband_role not in after.roles
        ):
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
