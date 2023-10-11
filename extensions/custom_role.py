import logging

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands


class CustomRoleButtons(discord.ui.View):
    def __init__(self, guild, role, admin_channel, user, existing_role, icon):
        super().__init__()
        self.guild = guild
        self.role = role
        self.admin_channel = admin_channel
        self.user = user
        self.existing_role = existing_role
        self.icon = icon
        self.value = None

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        trade_locked_role = discord.utils.get(
            self.guild.roles, name="Trade Locked"
        )
        if trade_locked_role:
            hoist_position = trade_locked_role.position - 1
            print(hoist_position)
            await self.role.edit(position=hoist_position)
        else:
            await self.admin_channel.respond(
                "Failed to find the 'Trade Locked' role."
            )
        await interaction.response.edit_message(view=None)
        await interaction.followup.send(
            content="Role successfully created!"
        )
        await self.user.add_roles(self.role, reason="Created a custom role")
        await self.user.send("Role successfully accepted and created!")
        existing_role = get_custom_role(self.user, existing_role)
        if existing_role:
            await existing_role.delete(reason="Creating a new custom role")
        self.value = True

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.red)
    async def deny_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.edit_message(view=None)
        await interaction.followup.send(
            content="Role Creation successfully denied!"
        )
        await self.role.delete(reason="Denied")
        await self.user.send("Your role creation was denied.")
        self.value = True


    @discord.ui.button(label="Show Icon", style=discord.ButtonStyle.grey)
    async def show_avatar(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_message(content=f"{self.icon}", ephemeral=True)
        self.value = True


class CustomRole(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.logger = logging.getLogger(f"EmployeeBot.{self.__class__.__name__}")
        self.bot = bot

    @app_commands.command(name="customrole", description="Create a custom role")
    @app_commands.describe(name="Name of your new custom role")
    @app_commands.describe(color="Hex color code of the role")
    @app_commands.describe(icon="URL to the icon image")
    @app_commands.describe(existing_role="The name of your current custom role.")
    async def slash_customrole(
        self,
        interaction: discord.Interaction,
        name: str,
        color: str,
        icon: discord.Attachment = None,
        existing_role: str = None,
    ):
        await interaction.response.defer(ephemeral=True)

        level_50_role_name = "Level 50"
        level_50_role = discord.utils.get(
            interaction.guild.roles, name=level_50_role_name
        )
        if level_50_role not in interaction.user.roles:
            await interaction.followup.send(
                "You have to be level 50 to use this command."
            )
            return

        guild = interaction.guild
        permissions = discord.Permissions.none()
        color_int = int(color, 16) 
        role = await guild.create_role(
            name=name, color=discord.Color(color_int), permissions=permissions
        )

        if icon:
            file = await icon.read()
            try:
                await role.edit(display_icon=file)
            except discord.errors.HTTPException as e:
                if e.status == 400:
                    await interaction.followup.send("The file is too big!")
                    return
                else:
                    await interaction.followup.send("An error occurred while setting the icon.")
                    return

        await interaction.followup.send(
            f"Custom role '{name}' has been sent for review!", ephemeral=True
        )

        embed = discord.Embed(title="Custom Role Creation", color=color_int)
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
        embed.add_field(name="User", value=interaction.user.mention, inline=False)
        embed.add_field(name="Role Name", value=name, inline=False)
        embed.add_field(name="Color", value=color, inline=False)

        if existing_role:
            embed.add_field(name="Replacing Role", value=existing_role, inline=False)

        admin_channel_id = 1121933856128376912
        admin_channel = self.bot.get_channel(admin_channel_id)
        await admin_channel.send(
            embed=embed,
            view=CustomRoleButtons(
                guild=interaction.guild,
                role=role,
                admin_channel=admin_channel,
                user=interaction.user,
                existing_role=existing_role,
                icon=icon,
            ),
        )

def get_custom_role(member, existing_role_name):
    if existing_role_name:
        for role in member.roles:
            if role.name.lower() == existing_role_name.lower():
                return role
    return None

async def download_image(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.read()
            else:
                raise ValueError("Failed to download the image")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CustomRole(bot))
