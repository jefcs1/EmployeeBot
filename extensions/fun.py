import asyncio
import logging

import aiosqlite
import discord
from discord import app_commands
from discord.ext import commands

from config import DB


class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.logger = logging.getLogger(f"EmployeeBot.{self.__class__.__name__}")
        self.bot = bot
        self.lock = asyncio.Lock()
        self._current_number: int | None = None
        self._last_sender_id: int | None = None

    async def process_number(
        self, number: int, sender_id: discord.Member, message: discord.Message
    ):
        if self._current_number is None:
            self._current_number = 0

        if sender_id == self._last_sender_id:
            await message.delete()
            return await message.channel.send(
                "You cannot send two numbers in a row", delete_after=3.0
            )

        if number != (self._current_number + 1):
            await message.delete()
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
            print(result)
        if result:
            self._last_sender_id = result[0]
            self._current_number = result[1]
        else:
            self._last_sender_id = None
            self._current_number = None

    async def store_current_data(self) -> None:
        async with aiosqlite.connect(DB) as conn:
            cursor = await conn.cursor()
            await cursor.execute(
                """INSERT INTO Counting (last_sender, last_number) VALUES (?, ?)
                                ON CONFLICT (last_sender, channel_id) DO 
                                SET last_sender = excluded.last_sender, last_number = excluded.last_number""",
                (self._current_number, self._last_sender_id),
            )
            await conn.commit()

    async def cog_unload(self) -> None:
        async with self.lock:
            await self.store_current_data()
            print("done")

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

            if self._current_number is None or self._last_sender_id is None:
                await self.refresh_current_data()

            await self.process_number(number, sender_id, message)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Fun(bot))
