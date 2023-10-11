import logging

import discord
from discord import app_commands
from discord.ext import commands

class Events(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.logger = logging.getLogger(f"EmployeeBot.{self.__class__.__name__}")
        self.bot=bot

    @app_commands.command(name="submit", description="Submit a file!")
    @app_commands.describe(attachment = "The attachment you want to submit.")
    async def submit(self, interaction:discord.Interaction, attachment: discord.Attachment):
        sub_channel = self.bot.get_channel(957350795274248292)
        embed = discord.Embed(title=f"Submission from {interaction.user.display_name}:", description="", color=0x86def2)
        await sub_channel.send(embed=embed)
        await sub_channel.send(attachment)
        await interaction.response.send_message("Your submission was recorded!", ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Events(bot))