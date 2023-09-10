import asyncio
import datetime
import logging

import discord  # type: ignore
from discord import app_commands
from discord.ext import commands

tradesite_links = {
    "Buff163": {"desc": "P2P | 2.5% Sale Fee", "link": "https://buff.163.com"},
    "Skinport": {"desc": "6-12% Sale Fee", "link": "https://skinport.com/"},
    "DMarket": {"desc": "7% Sale Fee", "link": "https://dmarket.com/"},
    "Skinbaron": {"desc": "1-15% Sale Fee", "link": "https://skinbaron.de/"},
    "CSMoney": {"desc": "5% Sale Fee", "link": "https://cs.money/"},
    "TradeIt": {"desc": "10% Sale Fee", "link": "https://tradeit.gg/"},
    "BuffMarket": {"desc": "P2P | 4.5% Sale Fee", "link": "https://buff.market/"},
    "CSDeals": {"desc": "2% Sale Fee", "link": "https://cs.deals/"},
    "BitSkins": {"desc": "~5% Sale Fee", "link": "https://bitskins.com/"},
    "CSGOFloat": {"desc": "P2P | 2% Sale Fee", "link": "https://csgofloat.com/"},
}


class PersistentSiteView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(SelectSite())


class SelectSite(discord.ui.Select):
    def __init__(self):

        options = []
        for label, value in tradesite_links.items():
            options.append(
                discord.SelectOption(
                    label=label, value=label, description=value.get("desc")
                )
            )

        super().__init__(
            placeholder="Click to view sites",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="persistentview:sites"
        )

    async def callback(self, interaction: discord.Interaction):
        selected_site = interaction.data["values"][0]
        selected_link = tradesite_links[selected_site]["link"]
        button = discord.ui.Button(
            label=selected_site, style=discord.ButtonStyle.link, url=selected_link
        )
        view = self.view
        view.clear_items()
        view.add_item(SelectSite())
        view.add_item(button)
        await interaction.response.edit_message(view=view)


class Links(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.logger = logging.getLogger(f"EmployeeBot.{self.__class__.__name__}")

    @app_commands.command(
        name="tradingsites",
        description="Gives you the official links to the most popular trading sites!",
    )
    async def slash_tradinglinks(self, interaction: discord.Interaction):
        view = PersistentSiteView()
        embed = discord.Embed(
            title="Trading Site Selection",
            description="Use the dropdown menu to view the links to the site you choose.",
            color=0x86DEF2,
        )
        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Links(bot))
