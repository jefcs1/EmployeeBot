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

role_thresholds = {
    "$50": 50,
    "$100": 100,
    "$250": 250,
    "$500": 500,
    "$750": 750,
    "$1,000": 1000,
    "$2,500": 2500,
    "$5,000": 5000,
    "$7,500": 7500,
    "$10,000": 10000,
    "$25,000": 25000,
    "$50,000": 50000,
    "$75,000": 75000,
    "$100,000": 100000,
    "$250,000": 250000,
    "$500,000": 500000,
    "$1,000,000": 1000000,
}


class ProfileInfo(NamedTuple):
    steam_id: int
    avatar: str
    username: str


class Inventory(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.logger = logging.getLogger(f"EmployeeBot.{self.__class__.__name__}")
        self.bot = bot
        self.verification_cache: Dict[int, ProfileInfo] = {}
        self.price_cache = {}
        self.command_usage = {}
        self.refresh_cache.start()

    def cog_load(self) -> None:
        self.refresh_cache.restart()

    def cog_unload(self):
        self.refresh_cache.cancel()

    @tasks.loop(hours=4.0)
    async def refresh_cache(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://prices.csgotrader.app/latest/prices_v6.json"
            ) as resp:
                raw_prices = await resp.text()
                prices = json.loads(raw_prices)
                self.price_cache = prices
        self.clear_old_records()

    def store_command_usage(self, user_id):
        self.command_usage[user_id] = time.time()

    def check_command_usage(self, user_id):
        if user_id in self.command_usage:
            if time.time() - self.command_usage[user_id] < 24 * 3600:
                return 1
        return 2

    def clear_old_records(self):
        current_time = time.time()
        self.command_usage = {
            user_id: timestamp
            for user_id, timestamp in self.command_usage.items()
            if current_time - timestamp < 24 * 3600
        }

    def add_to_cache(self, discord_user_id: int, entry: ProfileInfo):
        self.verification_cache[discord_user_id] = entry

    def remove_from_cache(self, discord_user_id: int) -> Optional[ProfileInfo]:
        try:
            return self.verification_cache.pop(discord_user_id, None)
        except KeyError:
            return None

    async def get_id(self, steam):
        match = re.search(
            r"https?://(www\.)?(steamcommunity\.com/)(profiles/|id/)([^/]+)", steam
        )
        if match:
            return match.group(4)
        else:
            return steam

    async def get_profile_info(
        self, steam_id: str, *, session: aiohttp.ClientSession
    ) -> Optional[ProfileInfo]:
        if steam_id.isdigit():
            async with session.get(
                "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/",
                params={"key": api_key, "steamids": steam_id},
            ) as resp:
                if resp.status != 200:
                    return None

                data = await resp.json()
                if data == {"response": {"players": []}}:
                    return None
                profileurl = data["response"]["players"][0]["avatarfull"]
                profilename = data["response"]["players"][0]["personaname"]
                return ProfileInfo(steam_id, profileurl, profilename)
        else:
            async with session.get(
                "http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/",
                params={"key": api_key, "vanityurl": steam_id},
            ) as resp:
                data = await resp.json()
                if "response" in data and data["response"].get("success", 0) == 1:
                    steam_id = data["response"]["steamid"]
                    return await self.get_profile_info(steam_id, session=session)
                else:
                    return None

    async def get_prices(self, steam_id, caching):
        if caching == True:
            params = {"key": steamweb_apikey, "steam_id": steam_id}
        else:
            params = {"key": steamweb_apikey, "steam_id": steam_id, "no_cache": 1}
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://www.steamwebapi.com/steam/api/inventory?sort=price_max",
                params=params,
            ) as resp:
                status = await self.process_status(resp.status)
                if status == 200:
                    data = await resp.json()
                    price = await self.add_prices(data)
                    return price
                else:
                    return status

    async def process_status(self, status):
        if status == 403:
            result = "Your inventory is private!"
        elif status == 500:
            result = f"There was an unexplained internal server error with the API. Please try again in a couple hours."
        elif status == 405:
            result = f"You have no items in your inventory!"
        elif status == 200:
            result = 200
        return result

    async def add_prices(self, data):
        steam_price = 0
        buff_price = 0
        num = len(data)
        for item in data:
            pricemedian = item.get("pricemedian", "N/A")
            steam_price += pricemedian
            name = item.get("markethashname", "N/A")
            item_data = self.price_cache.get(name)
            if item_data is not None:
                buff_data = item_data.get("buff163")
                if buff_data is not None:
                    starting_at = buff_data.get("starting_at")
                    item_price = starting_at.get("price")
                else:
                    buff_data = None
            else:
                item_data = None
            if item_price is not None:
                buff_price += item_price
        return round(buff_price, 2), round(steam_price, 2), num

    @commands.command()
    async def link(self, ctx, steam: Optional[str]):
        member = ctx.author

        async with aiosqlite.connect(DB) as conn:
            cursor = await conn.cursor()
            await cursor.execute(
                """SELECT steam_id FROM Inventories WHERE discord_id = ?""",
                (member.id,),
            )
            result = await cursor.fetchone()

        if result is None:
            if not steam:
                linkEmbed = discord.Embed(
                    title="How to link your account:",
                    description="**Link command**\n`!link <steamid>`\n`!link <steam profile link>`",
                    color=0x86DEF2,
                )
                linkEmbed.set_author(
                    name="TC Employee Steam Verification",
                    icon_url=self.bot.user.display_avatar,
                )
                await ctx.send(embed=linkEmbed)
                return
            else:
                id = await self.get_id(steam)

            if id is None:
                await ctx.send(
                    f"{ctx.author.mention}, an Invalid Steam ID or URL was provided."
                )
                return

            async with aiohttp.ClientSession() as session:
                current_profile_info = await self.get_profile_info(id, session=session)
                if current_profile_info is None:
                    await ctx.send(
                        f"{ctx.author.mention}, I can't get information on this profile. Check that your Steam ID is correct."
                    )

            cached_profile = self.verification_cache.get(ctx.author.id)

            if cached_profile is None:
                self.add_to_cache(ctx.author.id, current_profile_info)
                verifyEmbed = discord.Embed(
                    title=f"Profile: {current_profile_info.username}",
                    description=f"Please make your steam name ```{current_profile_info.username}-TC```\n[Click Here](https://steamcommunity.com/profiles/{current_profile_info.steam_id}/edit) to do so.",
                    color=0x86DEF2,
                )
                verifyEmbed.add_field(
                    name="After you're done, rerun the same `!link` command as before",
                    value="*Do not add a space between your name and `-TC`*",
                    inline=False,
                )
                verifyEmbed.add_field(
                    name="Not your account?",
                    value="Make sure you provided the correct Steam ID or account link.",
                    inline=False,
                )
                verifyEmbed.add_field(
                    name="Not sure what to do?",
                    value="[Click on this video to see instructions](https://fretgfr.com/u/CELNjn.mp4)",
                    inline=False,
                )
                verifyEmbed.set_author(
                    name="TC Employee Steam Verification",
                    icon_url=self.bot.user.display_avatar,
                )
                verifyEmbed.set_thumbnail(url=current_profile_info.avatar)

                return await ctx.send(embed=verifyEmbed)

            if cached_profile.steam_id != current_profile_info.steam_id:
                return await ctx.send(
                    f"{ctx.author.mention}, please use only one account while linking."
                )

            if current_profile_info.username != f"{cached_profile.username}-TC":
                return await ctx.send(
                    f"{ctx.author.mention}, please make your steam name ```{cached_profile.username}-TC```"
                )

            else:
                async with aiosqlite.connect(DB) as conn:
                    cursor = await conn.cursor()

                    await cursor.execute(
                        """INSERT INTO Inventories (discord_id, steam_id) VALUES (?, ?)""",
                        (
                            ctx.author.id,
                            current_profile_info.steam_id,
                        ),
                    )

                    await conn.commit()

                successEmbed = discord.Embed(
                    title="Verification Successful",
                    description="You may remove TC from your steam name.\nYou may now use the `!inv` command.",
                    color=0x86DEF2,
                )
                successEmbed.set_author(
                    name="TC Employee Steam Verification",
                    icon_url=self.bot.user.display_avatar,
                )

                await ctx.send(embed=successEmbed)
                discord_id = ctx.author.id
                self.remove_from_cache(discord_id)

        else:
            await ctx.send(
                f"{ctx.author.mention}, your account is already linked!\nType `!unlink` to link a different account."
            )

    @commands.command(aliases=["value"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def inv(
        self,
        ctx,
        member: discord.Member = None,
    ):
        for_other = True
        if member is None:
            member = ctx.author
            for_other = False

        result = self.check_command_usage(member.id)
        if result == 1:
            caching = False
        else:
            caching = True

        async with aiosqlite.connect(DB) as conn:
            cursor = await conn.cursor()

            await cursor.execute(
                """SELECT steam_id FROM Inventories WHERE discord_id = ?""",
                (member.id,),
            )
            result = await cursor.fetchone()

        if result is None:
            linkEmbed = discord.Embed(
                title="Please link your steam account first.",
                description="Link your steam with `!link` first before checking your inventory value.",
                color=0x86DEF2,
            )
            linkEmbed.set_author(
                name="TC Employee Inventory Value",
                icon_url=self.bot.user.display_avatar,
            )
            await ctx.send(embed=linkEmbed)
            return
        else:
            steam_id = result[0]
        msg = await ctx.send("Searching... (This may take a while)")
        prices = await self.get_prices(steam_id, caching)
        if isinstance(prices[0], float) and isinstance(prices[1], float):
            assigned_role = None
            if for_other == False:
                for role, threshold in role_thresholds.items():
                    if prices[1] > prices[0]:
                        if prices[1] >= threshold:
                            assigned_role = role
                    else:
                        if prices[0] >= threshold:
                            assigned_role = role
                if assigned_role is not None:
                    role_object = discord.utils.get(ctx.guild.roles, name=assigned_role)
            invEmbed = discord.Embed(
                title=f"{member.display_name}'s Inventory",
                description=f"{member.mention}",
                color=0x86DEF2,
            )
            invEmbed.add_field(
                name="Steam Inventory Value",
                value=f"\n**{prices[2]}** Items worth **${'{:,.2f}'.format(prices[1])}**",
                inline=False,
            )
            invEmbed.add_field(
                name="Buff163 Inventory Value",
                value=f"\n**{prices[2]}** Items worth **${'{:,.2f}'.format(prices[0])}**",
                inline=False,
            )
            if assigned_role is not None:
                if role_object not in ctx.author.roles:
                    invEmbed.add_field(
                        name="New Role",
                        value=f"You were given the role {role_object.mention}!",
                        inline=False,
                    )
                    await member.add_roles(role_object)
            invEmbed.set_author(
                name="TC Employee Inventory Value",
                icon_url=self.bot.user.avatar,
            )
            invEmbed.set_thumbnail(url=member.avatar)
            await msg.edit(embed=invEmbed, content=None)
        else:
            await ctx.send(content=f"{prices}")
        self.store_command_usage(member.id)

    @commands.command()
    async def unlink(self, ctx):
        discord_id = ctx.author.id

        async with aiosqlite.connect(DB) as conn:
            cursor = await conn.cursor()

            await cursor.execute(
                "DELETE FROM Inventories WHERE discord_id = ?", (discord_id,)
            )
            await conn.commit()

        await ctx.send(
            f"{ctx.author.mention}, your account has been successfully unlinked, or you didn't have an account linked."
        )

    @commands.command()
    async def restart(self, ctx):
        discord_id = ctx.author.id
        self.remove_from_cache(discord_id)
        await ctx.send("Your linking proccess has been restarted.")

    @inv.error
    async def inv_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            return await ctx.send(
                f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds."
            )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Inventory(bot))
