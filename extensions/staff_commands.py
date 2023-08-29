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
            await interaction.response.send_message("Creation Complete", ephemeral=True)
        while True:
            category_name = f"Members: {guild.member_count}"
            await category.edit(name=category_name)

            await asyncio.sleep(300)

    @app_commands.command(name="message", description="Message a member with an official TC Embed")
    @app_commands.describe(user="The user you want to message.")
    @app_commands.describe(message="The main message you want to send.")
    @app_commands.describe(reason="The reason for this message.")
    @app_commands.choices(reason=[app_commands.Choice(name='Misuse of Trading Channels', value=1), app_commands.Choice(name='Breaking Server Rules in Chat', value=2)])
    async def message(self, interaction:discord.Interaction, user: discord.Member, message:str, reason:app_commands.Choice[int]):
        
        message_embed =discord.Embed(title="This is a Direct Message from the Traders Compound Staff:", description=f'"{message}"', color = 0x86def2)
        message_embed.add_field(name="Reason for message:", value = f"`{reason.name}`")
        message_embed.set_author(name=interaction.user.global_name, icon_url = interaction.user.avatar)
        message_embed.set_footer(text="This message can't be replied to")

        await user.send(embed=message_embed)

        await interaction.response.send_message(f"Message succesfully sent to {user.name}!", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(StaffCommands(bot))
