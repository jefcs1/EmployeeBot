import asyncio
import logging

import aiosqlite
import discord
from discord import app_commands
from discord.ext import commands

from config import DB, admin_id, manager_id, founder_id


class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.logger = logging.getLogger(f"EmployeeBot.{self.__class__.__name__}")
        self.bot = bot
        self.lock = asyncio.Lock()
        self._current_number: int | None = None
        self._last_sender_id: int | None = None
        self.wrong_numbers: int = 0

    async def process_number(
        self, number: int, sender_id: discord.Member, message: discord.Message
    ):
        if sender_id == self._last_sender_id:
            await message.delete()
            return await message.channel.send(
                "You cannot send two numbers in a row", delete_after=3.0
            )
        if self._current_number==None:
            self._current_number=0
        if number != (self._current_number + 1):
            if self.wrong_numbers>=5:
                await message.delete()
                self.wrong_numbers=0
                return await message.channel.send(
                    f"The correct number is {self._current_number+1}", delete_after=3.0
                )
            else:
                await message.delete()
                self.wrong_numbers=self.wrong_numbers+1
                return await message.channel.send(
                    "That is not the correct number.", delete_after=3.0
                )

        self._current_number = number
        self._last_sender_id = sender_id

        if number in [
            10,
            69,
            100,
            420,
            500,
            1_000,
            5_000,
            10_000,
            25_000,
            50_000,
            69_420,
            75_000,
            100_000,
        ]:
            await message.pin()

    async def refresh_current_data(self) -> None:
        async with aiosqlite.connect(DB) as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT last_sender, last_number FROM Counting")
            result = await cursor.fetchone()
            await conn.commit()
        if result:
            self._last_sender_id = result[0]
            self._current_number = result[1]

    async def store_current_data(self) -> None:
        async with aiosqlite.connect(DB) as conn:
            cursor = await conn.cursor()
            await cursor.execute(
                """UPDATE Counting SET last_number = ?, last_sender = ?""",
                (self._current_number, self._last_sender_id),
            )
            await conn.commit()

    async def cog_unload(self) -> None:
        async with self.lock:
            await self.store_current_data()

    async def cog_load(self) -> None:
        async with self.lock:
            await self.refresh_current_data()

    @app_commands.command(name="bing", description="For MaDiT")
    async def slash_bing(self, interaction: discord.Interaction):
        await interaction.response.send_message("Chilling! :icecream:")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != 1157707729268392007:
            return
        if message.author == self.bot.user:
            return

        async with self.lock:
            try:
                number = int(message.content)
            except ValueError:
                await message.delete()
                return await message.channel.send(
                    f"Your message must be a number.", delete_after=2.0
                )

            sender_id = message.author.id

            await self.process_number(number, sender_id, message)
    
    @commands.command(name="setnum", description="Sets the current info for counting to the correct info")
    @commands.has_any_role(
        manager_id,
        admin_id,
        founder_id
    )
    async def setnum(self, ctx):
        channel=self.bot.get_channel(1157707729268392007)
        async for message in channel.history(limit=1):
            num=message.content
            id=message.author.id
            await Fun.cog_unload(self)
            async with aiosqlite.connect(DB) as conn:
                cursor = await conn.cursor()
                await cursor.execute(
                    """UPDATE Counting SET last_number = ?, last_sender = ?""",
                    (num, id),
                )
                await conn.commit()
            await Fun.cog_load(self)
            await ctx.send("Done!")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Fun(bot))
