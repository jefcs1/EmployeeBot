import logging
import aiohttp
from typing import NamedTuple, Dict, Optional, Union
import discord
import typing
from PIL import Image
import aiosqlite
from config import DB, api_key, steamweb_apikey
import re
from discord.ext import commands

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

    def add_to_cache(self, discord_user_id: int, entry: ProfileInfo):
        self.verification_cache[discord_user_id] = entry

    def remove_from_cache(self, discord_user_id: int) -> Optional[ProfileInfo]:
        try:
            return self.verification_cache.pop(discord_user_id, None)
        except KeyError:
            return None

    async def get_id(self, steam):
        if re.match(r"^[a-zA-Z0-9_-]+$", steam):
            return steam

        match = re.search(r"(?:https?://)?steamcommunity\.com/(?:profiles/(\d+)|id/(\w+))", steam)
        if match:
            if match.group(1):
                return match.group(1)
            elif match.group(2):
                return match.group(2)

        if re.match(r"^\d+$", steam):
            return steam
        return None

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
                profileurl = data["response"]["players"][0]["avatarfull"]
                profilename = data["response"]["players"][0]["personaname"]
                return ProfileInfo(steam_id, profileurl, profilename)
        else:
            async with session.get(
                "http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/",
                params={"key": api_key, "vanityurl": steam_id},
            ) as resp:
                data = await resp.json()
                if 'response' in data and data['response'].get('success', 0) == 1:
                    steam_id = data["response"]["steamid"]
                    return await self.get_profile_info(steam_id, session=session)
                else:
                    return None

    @commands.command()
    async def link(self, ctx, steam: Optional[str]):
        if not steam:
            linkEmbed = discord.Embed(
                title="How to link your account:",
                description="**Link command**\n`-link <steamid>`\n`-link <steam profile link>`",
                color=0x86DEF2,
            )
            linkEmbed.set_author(
                name="TC Employee Steam Verification",
                icon_url=self.bot.user.display_avatar,
            )
            await ctx.send(embed=linkEmbed)
        else:
            id = await self.get_id(steam)

        if id is None:
            await ctx.send(f"{ctx.author.mention}, and Invalid Steam ID or URL was provided.")
            return

        async with aiohttp.ClientSession() as session:
            current_profile_info = await self.get_profile_info(id, session=session)
            if current_profile_info is None:
                await ctx.send(f"{ctx.author.mention}, I can't get information on this profile.")

        cached_profile = self.verification_cache.get(ctx.author.id)

        if cached_profile is None:
            self.add_to_cache(ctx.author.id, current_profile_info)
            verifyEmbed = discord.Embed(
                title=f"Profile: {current_profile_info.username}",
                description=f'If this is your account please add "-TC"\nto the end of your Steam name to prove ownership.\n[Click Here](https://steamcommunity.com/profiles/{current_profile_info.steam_id}/edit) to change it and rerun the `!link` command.',
                color=0x86DEF2,
            )
            verifyEmbed.add_field(
                name="Not your account?",
                value="Make sure you provided the correct Steam ID or account link.",
            )
            verifyEmbed.set_author(
                name="TC Employee Steam Verification",
                icon_url=self.bot.user.display_avatar,
            )
            verifyEmbed.set_thumbnail(url=current_profile_info.avatar)
            verifyEmbed.set_footer(text="See Image Below For an Example")

            return await ctx.send(embed=verifyEmbed)

        if cached_profile.steam_id != current_profile_info.steam_id:
            return await ctx.send(f"{ctx.author.mention}, please use only one account while linking.")

        if current_profile_info.username != f"{cached_profile.username}-TC":
            return await ctx.send(f"{ctx.author.mention}, please add '-TC' to the end of your steam name")

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

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def inv(self, ctx, member: discord.Member = None):
        """Gets the inventory value of a Steam Account."""
        total_price = 0

        if member is None:
            member = ctx.author

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
                    color=0x86def2,
                )
                linkEmbed.set_author(
                    name="TC Employee Inventory Value",
                    icon_url=self.bot.user.display_avatar,
                )
                await ctx.send(embed=linkEmbed)
                return
            else:
                steam_id = result[0]
                msg = await ctx.send("Searching...")
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        "https://www.steamwebapi.com/steam/api/inventory?game=csgo&sort=price_max&currency=USD",
                        params={"key": steamweb_apikey, "steam_id": steam_id},
                    ) as resp:
                        if resp.status == 403:
                            await msg.edit(content="Your inventory is private!")
                            return
                        elif resp.status == 200:
                            data = await resp.json()
                            total_price = 0 
                            for item in data:
                                pricemedian = item.get("pricemedian", "N/A")
                                total_price += pricemedian

                        assigned_role = None
                        for role, threshold in role_thresholds.items():
                            if total_price >= threshold:
                                assigned_role = role

                        if assigned_role:
                            role_object = discord.utils.get(
                                ctx.guild.roles, name=assigned_role
                            )
                            if role_object not in ctx.author.roles:
                                await ctx.author.add_roles(role_object)

                            invEmbed = discord.Embed(
                                title=f"{ctx.author.display_name}'s Inventory",
                                description=f"{ctx.author.mention}",
                                color=0x86DEF2,
                            )
                            invEmbed.add_field(
                                name="CSGO Inventory Value",
                                value=f"\n**{len(data)}** Items worth **${round(total_price,2)}**",
                            )
                            if role_object not in ctx.author.roles:
                                invEmbed.add_field(
                                    name="New Role",
                                    value=f"You were given the role {role_object.mention}!",
                                    inline=False,
                                )
                            invEmbed.set_author(
                                name="TC Employee Inventory Value",
                                icon_url=self.bot.user.avatar,
                            )
                            invEmbed.set_thumbnail(url=ctx.author.avatar)
                            await msg.edit(embed=invEmbed, content=None)

        else:
            async with aiosqlite.connect(DB) as conn:
                cursor = await conn.cursor()

                await cursor.execute(
                    """SELECT steam_id FROM Inventories WHERE discord_id = ?""",
                    (member.id,),
                )
                result = await cursor.fetchone()

                if result is None:
                    FriendLinkEmbed = discord.Embed(
                        title="Account not linked!",
                        description=f"It seems like {member.mention} does not have an account linked with me.\nPlease ask them to link their account!",
                        color=0x86DEF2,
                    )
                    await ctx.send(embed=FriendLinkEmbed)
                else:
                    msg = await ctx.send("Checking Value...")
                    steam_id=result[0]

                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        "https://www.steamwebapi.com/steam/api/inventory?game=csgo&sort=price_max&currency=USD",
                        params={"key": steamweb_apikey, "steam_id": steam_id},
                    ) as resp:
                        if resp.status == 403:
                            await msg.edit(content="Your inventory is private!")
                            return
                        elif resp.status == 200:
                            data = await resp.json()
                            total_price = 0 
                            for item in data:
                                pricemedian = item.get("pricemedian", "N/A")
                                total_price += pricemedian

                            invEmbed = discord.Embed(
                                title=f"{member.display_name}'s Inventory",
                                description=f"{member.mention}",
                                color=0x86DEF2,
                            )
                            invEmbed.add_field(
                                name="CSGO Inventory Value",
                                value=f"\n**{len(data)}** Items worth **${round(total_price,2)}**",
                            )
                            invEmbed.set_author(
                                name="TC Employee Inventory Value",
                                icon_url=self.bot.user.avatar,
                            )
                            invEmbed.set_thumbnail(url=member.avatar)
                            await msg.edit(embed=invEmbed, content=None)

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
            await ctx.send(f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Inventory(bot))
