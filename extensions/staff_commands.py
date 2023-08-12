import asyncio
import logging

import discord
from discord import app_commands
from discord.ext import commands


class StaffCommands(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.logger = logging.getLogger(f"EmployeeBot.{self.__class__.__name__}")

    @app_commands.command(
        name="membercategory",
        description="Creates category that counts the server members",
    )
    async def membercategory(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "Sorry, only admins can use this command."
            )
            return
        else:
            guild = self.bot.get_guild(interaction.guild_id)
            category_name = "Members: " + str(guild.member_count)
            category = await guild.create_category(category_name)
            await category.edit(position=0)
            await interaction.response.send_message("Creation Complete")
        while True:
            category_name = f"Members: {guild.member_count}"
            await category.edit(name=category_name)

            await asyncio.sleep(300)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(StaffCommands(bot))
