import datetime
import logging

import arrow
import discord  # type: ignore
from discord import app_commands
from discord.ext import commands


class Info(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.logger = logging.getLogger(f"EmployeeBot.{self.__class__.__name__}")
        self.bot = bot

    @app_commands.command(
        name="userinfo", description="Gives you information on a specified user!"
    )
    async def slash_userinfo(
        self, interaction: discord.Interaction, member: discord.Member
    ):
        if member == None:
            member = interaction.user
        roles = sorted(member.roles, key=lambda x: x.position, reverse=True)
        userEmbed = discord.Embed(
            title="User Info",
            description=f"{member.mention}",
            timestamp=datetime.datetime.now(),
            color=0x86DEF2,
        )
        userEmbed.clear_fields()
        userEmbed.set_author(
            name=f"{member.name}#{member.discriminator}", icon_url=member.avatar
        )
        userEmbed.set_thumbnail(url=member.avatar)
        userEmbed.add_field(name="**ID**", value=member.id, inline=False)
        userEmbed.add_field(
            name="**Discord account creation date:**",
            value=f"{member.created_at.strftime('%a, %B %d, %Y, %I:%M %p')}, ({arrow.get(member.created_at).humanize()})",
            inline=False,
        )
        userEmbed.add_field(
            name="**Server join date:**",
            value=f"{member.joined_at.strftime('%a, %B %d, %Y, %I:%M %p')}, ({arrow.get(member.joined_at).humanize()})",
            inline=False,
        )
        if member.premium_since is not None:
            userEmbed.add_field(name="Nitro Booster?", value="Yes", inline=False)
        else:
            userEmbed.add_field(name="Nitro Booster?", value="No", inline=False)
        userEmbed.add_field(
            name=f"Roles ({len(roles)-1})",
            value=", ".join(
                [
                    role.mention
                    for role in roles
                    if role != interaction.guild.default_role
                ]
            ),
            inline=False,
        )
        userEmbed.set_footer(text="This bot was made by jef :)")
        await interaction.response.send_message(embed=userEmbed)

    @app_commands.command(
        name="serverinfo", description="Displays information about the server"
    )
    async def slash_serverinfo(self, interaction: discord.Interaction):
        serverEmbed = discord.Embed(
            title="Server Info", timestamp=datetime.datetime.now(), color=0x86DEF2
        )
        serverEmbed.clear_fields()
        serverEmbed.set_author(
            name=interaction.guild.name, icon_url=interaction.guild.icon.url
        )
        serverEmbed.set_thumbnail(url=interaction.guild.icon)
        serverEmbed.add_field(name="**ID**", value=interaction.guild.id, inline=False)
        serverEmbed.add_field(
            name="**Owner**", value="<@267768698054377473>", inline=False
        )
        serverEmbed.add_field(
            name="**Created Date**",
            value=interaction.guild.created_at.strftime("%a, %B %d, %Y, %I:%M %p"),
            inline=False,
        )
        serverEmbed.add_field(
            name="**Member count**", value=interaction.guild.member_count, inline=False
        )
        serverEmbed.add_field(
            name="**Boosts**",
            value=f"Boost Level: {interaction.guild.premium_tier} \n Boosts: {interaction.guild.premium_subscription_count}",
            inline=False,
        )
        serverEmbed.add_field(
            name="**Roles**", value=len(interaction.guild.roles), inline=False
        )
        serverEmbed.add_field(
            name="**Channels**",
            value=f"Text Channels: {len(interaction.guild.text_channels)} \n Voice Channels: {len(interaction.guild.voice_channels)} \n Categories: {len(interaction.guild.categories)}",
            inline=False,
        )
        non_animated_emojis = [
            emoji for emoji in interaction.guild.emojis if not emoji.animated
        ]
        moji_string = " ".join(str(emoji) for emoji in non_animated_emojis)
        total_emoji_count = len(interaction.guild.emojis)
        regular_emoji_count = len(non_animated_emojis)
        animated_emoji_count = len(interaction.guild.emojis) - regular_emoji_count
        serverEmbed.add_field(
            name="**Emojis**",
            value=f"Regular: {regular_emoji_count}\nAnimated: {animated_emoji_count}\nTotal: {total_emoji_count}/{interaction.guild.emoji_limit}",
            inline=False,
        )
        serverEmbed.set_footer(text="This bot was made by jef :)")
        await interaction.response.send_message(embed=serverEmbed)

    @app_commands.command(name="ping", description="Returns the bot's latency")
    async def slash_ping(self, interaction: discord.Interaction):
        """Pong!"""
        # have to convert code
        latency = round(self.bot.latency * 1000)
        if latency < 250:
            color = discord.Color.blue()
        elif latency < 450 and latency > 250:
            color = discord.Color.green()
        elif latency < 600 and latency > 450:
            color = discord.Color.orange()
        elif latency < 800 and latency > 600:
            color = discord.Color.red()
        else:
            color = discord.Color.dark_red()
        embed = discord.Embed(
            title=":ping_pong: Pong!",
            color=color,
            timestamp=datetime.datetime.utcnow(),
        )
        embed.add_field(name="Latency", value=f"```json\n{latency} ms```", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="avatar", description="Displays the specified user's avatar"
    )
    @app_commands.describe(member="The member who's avatar you would like to see")
    async def slash_avatar(
        self, interaction: discord.Interaction, member: discord.Member
    ):
        if member == None:
            member = interaction.user

        memberAvatar = member.avatar.url

        avaEmbed = discord.Embed(title=f"{member.name}'s Avatar:", color=0x86DEF2)
        avaEmbed.set_image(url=memberAvatar)
        await interaction.response.send_message(embed=avaEmbed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Info(bot))
