import json
import logging
import re
from typing import Dict, NamedTuple, Optional

import aiohttp
import aiosqlite
import discord
import time
from discord.ext import commands, tasks

from config import DB, api_key, steamweb_apikey


class Inventory2(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.logger = logging.getLogger(f"EmployeeBot.{self.__class__.__name__}")
        self.bot = bot
    #     self.price_cache = {}
    #     self.command_usage = {}
    #     self.refresh_cache.start()

    # def cog_load(self) -> None:
    #     self.refresh_cache.restart()

    # def cog_unload(self):
    #     self.refresh_cache.cancel()

    # @tasks.loop(hours=4.0)
    # async def refresh_cache(self):
    #     async with aiohttp.ClientSession() as session:
    #         async with session.get(
    #             "https://prices.csgotrader.app/latest/prices_v6.json"
    #         ) as resp:
    #             raw_prices = await resp.text()
    #             prices = json.loads(raw_prices)
    #             self.price_cache = prices
    #             self.clear_old_records()

    # def store_command_usage(self, user_id):
    #     self.command_usage[user_id] = time.time()

    # def check_command_usage(self, user_id):
    #     if user_id in self.command_usage:
    #         if time.time() - self.command_usage[user_id] < 24 * 3600:
    #             return True
    #     return False

    # def clear_old_records():
    #     current_time = time.time()
    #     command_usage = {user_id: timestamp for user_id, timestamp in command_usage.items() 
    #                         if current_time - timestamp < 24 * 3600}

    # async def get_prices(self, steam_id, caching):
    #     if caching == True: 
    #         params = {"key": steamweb_apikey, "steam_id": steam_id}
    #     else:
    #         params = {"key": steamweb_apikey, "steam_id": steam_id, "no_cache": True}
    #     async with aiohttp.ClientSession() as session:
    #         async with session.get(
    #             "https://www.steamwebapi.com/steam/api/inventory?sort=price_max",
    #             params=params,
    #         ) as resp:
    #             status = await self.process_status(resp.status)
    #             if status == 200:
    #                 data=await resp.json()
    #                 price = await self.add_prices(data)
    #                 return price
    #             else:
    #                 return status

    # async def process_status(self, status):
    #     if status == 403:
    #         result = "Your inventory is private!"
    #     elif status == 500:
    #         result = f"There was an unexplained internal server error with the API. Please try again in a couple hours."
    #     elif status == 405:
    #         result = f"You have no items in your inventory!"
    #     elif status == 200:
    #         result = 200
    #     return result

    # async def add_prices(self, data):  # might not work
    #     steam_price = 0
    #     buff_price = 0
    #     for item in data:
    #         pricemedian = item.get("pricemedian", "N/A")
    #         steam_price += pricemedian
    #         name = item.get("markethashname", "N/A")
    #         item_data=self.price_cache.get(name)
    #         if item_data is not None:
    #             buff_data = item_data.get("buff163")
    #             if buff_data is not None:
    #                 starting_at = buff_data.get("starting_at")
    #                 item_price = starting_at.get("price")
    #             else:
    #                 buff_data=None
    #         else:
    #             item_data=None
    #         if item_price is not None:
    #             buff_price += item_price
    #     return buff_price, steam_price

    # @commands.command(aliases=["value2"])
    # @commands.cooldown(1, 10, commands.BucketType.user)
    # async def inv2(
    #     self,
    #     ctx,
    #     member: discord.Member = None,
    # ):
    #     if member is None:
    #         member = ctx.author

    #     if self.check_command_usage(member.id):
    #         caching=False
    #     else:
    #         caching=True

    #     async with aiosqlite.connect(DB) as conn:
    #         cursor = await conn.cursor()

    #         await cursor.execute(
    #             """SELECT steam_id FROM Inventories WHERE discord_id = ?""",
    #             (member.id,),
    #         )
    #         result = await cursor.fetchone()

    #     if result is None:
    #         linkEmbed = discord.Embed(
    #             title="Please link your steam account first.",
    #             description="Link your steam with `!link` first before checking your inventory value.",
    #             color=0x86DEF2,
    #         )
    #         linkEmbed.set_author(
    #             name="TC Employee Inventory Value",
    #             icon_url=self.bot.user.display_avatar,
    #         )
    #         await ctx.send(embed=linkEmbed)
    #         return
    #     else:
    #         steam_id = result[0]
    #     msg = await ctx.send("Searching... (This may take a while)")
    #     prices = await self.get_prices(steam_id, caching=caching)
    #     if isinstance(prices[0], float) and isinstance(prices[1], float):
    #         await msg.edit(content=f"{prices[0]}\n{prices[1]}")
    #     else:
    #         await ctx.send(content=f"{prices}")
    #     self.store_command_usage(member.id)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Inventory2(bot))
