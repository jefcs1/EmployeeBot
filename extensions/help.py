import asyncio
import datetime
import logging

import discord  # type: ignore
from discord import app_commands
from discord.ext import commands

class HelpTypes(discord.ui.Select):
    def __init__(self):
        super().__init__()
        self.help_sections = {
            "Information Commands": {
                "desc": "Displays all of the Bot's information-related commands",
                "embed": discord.Embed(
                    title="Information Commands",
                    description="All of the information commands the bot has!",
                ).add_field(
                    name="**Info Commands**",
                    value="</tradingsites:1123729246146277487> -> Displays the official links of popular trading sites\n</userinfo:1123690824132218933> -> Displays information about a server member\n</serverinfo:1123692973058707591> -> Displays information about the server!\n</avatar:1123766305980424214> -> Displays a specified user's avatar\n</overpay:1123766305980424212> -> Calculates how much you need to overpay\n</rules:1123724764192723085> -> Displays the server's rules\n</tradingchannels:1123766305980424213> -> Tells a user how to use the trading channels!\n</donate:1123774312822870038> -> Lets you know how to donate to the server!\n</boost:1123690824132218931> -> Lets you know how to boost the server!\n</topgg:1140006715077701663> -> Sends the Top.gg Server Voting link\n</ping:1123690824132218934> -> Displays the bot's latency\n</leaderboardbumps:1140006739459190856> Shows you the users with the most bumps\n</bumps:1140006739459190855> -> Shows you 5 most recent bumps\n</nextbump:1140006739459190857> -> Tells you when the next bump is",
                    inline=False,
                ),
            },
            "Functional Commands": {
                "desc": "Displays the Bot's function-related commands",
                "embed": discord.Embed(
                    title="Functional Commands",
                    description="All of the function commands the bot has!",
                    color=0x86DEF2,
                ).add_field(
                    name="**Function Commands**",
                    value="</customrole:1124462872949424279> -> Allows you to create your own custom role\n</createautopost:1125656573902065674> -> Lets you auto-post your trade advertisement\n`!link` -> Verify ownership of your Steam Account\n`!inv` -> Checks your CSGO Inventory Value\n`!unlink` -> Allows you to unlink your Steam Account\n`!restart` -> Lets you restart the linking process if you made a mistake.",
                ),
            },
            "Fun Commands": {
                "desc": "Displays the Bot's fun commands",
                "embed": discord.Embed(
                    title="Fun Commands",
                    description="All of the fun commands the bot has!",
                    color=0x86DEF2,
                ).add_field(
                    name="**Fun Commands**",
                    value="</bing:1124820390347284560> -> Chilling!",
                ),
            },
        }

        options = []
        for label, value in self.help_sections.items():
            options.append(
                discord.SelectOption(
                    label=label, value=label, description=value.get("desc")
                )
            )

        super().__init__(
            placeholder="Choose the type of command...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        selected_site = interaction.data["values"][0]
        selected_embed = self.help_sections[selected_site]["embed"]
        await interaction.response.send_message(embed=selected_embed, ephemeral=True)


class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()

        self.add_item(HelpTypes())


class Help(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.logger = logging.getLogger(f"EmployeeBot.{self.__class__.__name__}")

    @app_commands.command(
        name="help",
        description="Lets you know what commands the bot uses, and what they do!",
    )
    async def slash_help(self, interaction: discord.Interaction):
        view = DropdownView()
        embed = discord.Embed(
            title="Command Type Selection",
            description="Use the dropdown menu to view the type commands you choose.",
            color=0x86DEF2,
        )
        embed.set_footer(text="This bot was made by jef :)\ncredit to fretgfr")
        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Help(bot))
