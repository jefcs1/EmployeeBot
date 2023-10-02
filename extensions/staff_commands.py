import asyncio
import logging
from datetime import timedelta

import discord
from discord import app_commands
from discord.ext import commands


def convert(time):
    pos = ["s", "m", "h", "d"]

    time_dict = {"s": 1, "m": 60, "h": 3600, "d": 3600 * 24}

    unit = time[-1]
    if unit not in pos:
        return -1
    try:
        val = int(time[:-1])
    except:
        return -2

    return val * time_dict[unit]


class StaffCommands(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.logger = logging.getLogger(f"EmployeeBot.{self.__class__.__name__}")
        self.message_content = None

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

    @commands.command()
    async def delnoedit(self, ctx, delay: str, message_link: str):
        try:
            message_link_parts = message_link.strip("/").split("/")
            if len(message_link_parts) != 7:
                await ctx.send("Invalid message link format.")
                return

            channel_id, message_id = map(int, message_link_parts[-3:])

            channel = self.bot.get_channel(channel_id)
            message = await channel.fetch_message(message_id)
            self.edited_message = message.content

            duration = convert(delay)

            if message:
                del_time = discord.utils.format_dt(
                    discord.utils.utcnow() + timedelta(seconds=duration), style="R"
                )
                m = await ctx.send(
                    f"I'll delete that at in {del_time}, if they don't edit the message."
                )
                await asyncio.sleep(duration)

                edited_message = await channel.fetch_message(message_id)
                if edited_message and edited_message.content != self.message_content:
                    await edited_message.delete()
                    await m.edit(content="Deleted the message.")
                else:
                    await m.edit(content="The message author edited their message.")
            else:
                await ctx.send("Message not found.")
        except Exception as e:
            print(e)

    @app_commands.command(
        name="message", description="Message a member with an official TC Embed"
    )
    @app_commands.describe(user="The user you want to message.")
    @app_commands.describe(message="The main message you want to send.")
    @app_commands.describe(reason="The reason for this message.")
    @app_commands.choices(
        reason=[
            app_commands.Choice(name="Misuse of Trading Channels", value=1),
            app_commands.Choice(name="Breaking Server Rules in Chat", value=2),
        ]
    )
    async def message(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        message: str,
        reason: app_commands.Choice[int],
    ):
        message_embed = discord.Embed(
            title="This is a Direct Message from the Traders Compound Staff:",
            description=f'"{message}"',
            color=0x86DEF2,
        )
        message_embed.add_field(name="Reason for message:", value=f"`{reason.name}`")
        message_embed.set_author(
            name=interaction.user.display_name, icon_url=interaction.user.avatar
        )
        message_embed.set_footer(text="This message can't be replied to")

        try:
            await user.send(embed=message_embed)
            await interaction.response.send_message(
                f"Message succesfully sent to {user.name}!", ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "I couldn't send a DM to this person", ephemeral=True
            )

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(StaffCommands(bot))
