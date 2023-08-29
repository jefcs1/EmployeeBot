import asyncio
import datetime
import logging
from datetime import date

import aiosqlite
import discord
from discord import app_commands
from discord.ext import commands, tasks


class TicketButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Open a Ticket",
        style=discord.ButtonStyle.green,
        emoji="<:tcticket:1126250062545166416>",
    )
    async def open_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer(ephemeral=True)

        opener = interaction.user

        guild = interaction.guild
        ticket_category_id = 1101507373467701290

        ticket_category = discord.utils.get(guild.categories, id=ticket_category_id)
        print(ticket_category)

        guild = interaction.guild
        for channel in guild.channels:
            if isinstance(channel, discord.TextChannel):
                if channel.topic == f"{interaction.user}'s Ticket":
                    await interaction.followup.send(
                        "You already have a ticket open", ephemeral=True
                    )
                    return

        staff_role_id = 984449432059789352
        support_role_id = 965931278610346084
        staff_role = interaction.guild.get_role(staff_role_id)
        support_role = interaction.guild.get_role(support_role_id)
        permission_overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            staff_role: discord.PermissionOverwrite(
                read_messages=True, send_messages=True, manage_messages=True
            ),
            support_role: discord.PermissionOverwrite(
                read_messages=True, send_messages=True, manage_messages=True
            ),
            interaction.user: discord.PermissionOverwrite(
                read_messages=True, send_messages=True
            ),
        }

        ticket_channel = await ticket_category.create_text_channel(
            name=f"Ticket: {interaction.user}",
            topic=f"{interaction.user}'s Ticket",
            overwrites=permission_overwrites,
        )

        TicketEmbed2 = discord.Embed(
            description="If a member of the staff team does not help you within 10 minutes,\nyou may ping a staff member once.",
            color=0x86DEF2,
        )
        TicketEmbed2.add_field(
            name='To close the ticket, click "Close the Ticket" below.', value="Thanks!"
        )

        await ticket_channel.send(
            content=f"Thank you for opening a ticket {interaction.user.mention}\nA {support_role.mention} member will be with you shortly.",
            embed=TicketEmbed2,
            view=CloseButton(opener),
        )
        await interaction.followup.send(
            "Your ticket was successfully created!", ephemeral=True
        )


class CloseButton(discord.ui.View):
    def __init__(self, opener):
        super().__init__(timeout=None)
        self.opener = opener

    @discord.ui.button(
        label="Close the Ticket",
        style=discord.ButtonStyle.red,
        emoji="<:tclock:1126250550493724734>",
    )
    async def close_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer(ephemeral=True)

        await interaction.followup.send(
            "Closing the ticket in a couple of seconds...", ephemeral=True
        )
        await asyncio.sleep(3)

        guild = interaction.guild
        staff_role_id = 984449432059789352
        support_role_id = 965931278610346084
        staff_role = interaction.guild.get_role(staff_role_id)
        support_role = interaction.guild.get_role(support_role_id)

        permission_overwrites = {
            guild.default_role: discord.PermissionOverwrite(
                read_messages=False, send_messages=False
            ),
            staff_role: discord.PermissionOverwrite(
                read_messages=True, send_messages=True, manage_messages=True
            ),
            support_role: discord.PermissionOverwrite(
                read_messages=True, send_messages=False
            ),
            self.opener: discord.PermissionOverwrite(
                read_messages=True, send_messages=False
            ),
        }

        await interaction.channel.edit(overwrites=permission_overwrites)

        closeEmbed = discord.Embed(
            title="Ticket Closed",
            description=f"This ticket was closed by {interaction.user.mention}\nOnly Staff Members can send messages.",
            color=0xFF0000,
        )
        await interaction.channel.send(embed=closeEmbed, view=DeleteButton())


class DeleteButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Delete the Ticket",
        style=discord.ButtonStyle.red,
        emoji="<:tccancel:1126251084592205845>",
    )
    async def delete_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.guild_permissions.administrator:
            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send(
                "Deleting the channel in a couple of seconds...", ephemeral=True
            )
            await asyncio.sleep(4)
            await interaction.channel.delete()
        else:
            await interaction.response.send_message(
                "Only administrators can use this button.", ephemeral=True
            )


class Tickets(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.logger = logging.getLogger(f"EmployeeBot.{self.__class__.__name__}")
        self.bot = bot

    @app_commands.command(name="ticket", description="Sends the ticket Embed")
    async def slash_ticket(self, interaction: discord.Interaction):
        TicketEmbed2 = discord.Embed(
            title="Traders Compound Tickets",
            description='To create a ticket, press the "Open a Ticket" button below.',
            color=0x86DEF2,
        )
        ticket_embed_channel = interaction.channel
        await interaction.response.send_message(
            "Ticket Embed Successfully sent!", ephemeral=True
        )
        await ticket_embed_channel.send(embed=TicketEmbed2, view=TicketButton())


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Tickets(bot))
