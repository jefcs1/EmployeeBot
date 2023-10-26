import logging
import asyncio
import discord
from config import DB
import aiosqlite
from discord import app_commands
from discord.ext import commands

    
class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.logger = logging.getLogger(f"EmployeeBot.{self.__class__.__name__}")
        self.bot = bot
        self.lock = asyncio.Lock()
        self._current_number: int | None = None
        self._last_sender: int | None = None
    
    async def process_number(self, number, sender, message):
        if number == self._current_number +1: 
            self._current_number = number
            if sender != self._last_sender_id:
                self._last_sender_id = sender
                if number in [10, 100, 500, 1000, 5000, 100000]:
                    await message.pin()
            else:
                await message.delete()
                msg=await message.channel.send(f"You cannot send two numbers in a row.")
                asyncio.sleep(1)
                await msg.delete()
        else:
            await message.delete()
            msg=await message.channel.send(f"That is not the correct number.")
            asyncio.sleep(1)
            await msg.delete()

    async def refresh_current_data(self) -> None:
        async with aiosqlite.connect(DB) as conn:
                cursor = await conn.cursor()
                await cursor.execute(
                    """SELECT last_sender, last_number FROM Counting""",
                )
                result = await cursor.fetchone()
        self._last_sender_id = result[0]
        self._current_number = result[1]

    async def store_current_data(self) -> None:
        async with aiosqlite.connect(DB) as conn:
            cursor = await conn.cursor()
            await cursor.execute(
                """INSERT INTO Counting (last_sender, last_number) VALUES (?, ?)
                                ON CONFLICT (last_sender, channel_id) DO 
                                SET last_sender = excluded.last_sender, last_number = excluded.last_number"""
                                (self.current_number, self._last_sender)
            )
            await conn.commit() 
    
    @property
    async def current_number(self) -> int:
        if self._current_number is None:
            await self.refresh_current_data()

        return self._current_number # type: ignore

    @property
    async def last_sender_id(self) -> int:
        if self._last_sender_id is None:
            await self.refresh_current_data()

        return self._last_sender_id # type: ignore

    async def cog_unload(self) -> None:
        await self.store_current_data()
    

    @app_commands.command(name="bing", description="For MaDiT")
    async def slash_bing(self, interaction: discord.Interaction):
        await interaction.response.send_message("Chilling! :icecream:")

    @commands.Cog.listener()
    async def on_message(self, message):
        if msg.channel.id != 1157707729268392007: return
        if message.author == self.bot.user: return
        
        async with self.lock:
            if message.content.isdigit():
                number = int(message.content)
                sender = message.author.id
                if self._current_number != None:
                    if self._last_sender != None:
                        await self.process_number(number, sender, message)
                    else:
                        Fun.current_number = number
                        Fun.last_sender_id = sender
                        await self.process_number(number, sender, message)
                else:
                    Fun.current_number = number
                    Fun.last_sender_id = sender
                    await self.process_number(number, sender, message)
            else:
                await message.delete()
                msg = await message.channel.send(f"Your message must be a number.")
                asyncio.sleep(1)
                await msg.delete()

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Fun(bot))
