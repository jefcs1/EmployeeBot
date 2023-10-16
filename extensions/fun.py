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
    #     self.lock = asyncio.Lock()
    #     self._current_number: int | None = None
    #     self.last_sender: int | None = None

    # async def get_current_number(self) -> tuple:
    #     async with aiosqlite.connect(DB) as conn:
    #             cursor = await conn.cursor()

    #             await cursor.execute(
    #                 """SELECT last_sender, last_number FROM Counting""",
    #             )
    #             result = await cursor.fetchone()
    #             return result
    
    # async def store_current_number(self) -> None:
    #     async with aiosqlite.connect(DB) as conn:
    #         cursor = await conn.cursor()
    #         await cursor.execute(
    #             """INSERT INTO Counting (last_sender, last_number) VALUES (?, ?)
    #                             ON CONFLICT (last_sender, channel_id) DO 
    #                             SET last_sender = excluded.last_sender, last_number = excluded.last_number"""
    #         )
    #         await conn.commit()

    @app_commands.command(name="bing", description="For MaDiT")
    async def slash_bing(self, interaction: discord.Interaction):
        await interaction.response.send_message("Chilling! :icecream:")

    # @commands.Cog.listener()
    # async def on_message(self, message):

    #     if message.channel.id != 1157707729268392007:
    #         return
    #     if message.author == self.bot.user:
    #         return

    #     if message.content.isdigit():
    #         number = int(message.content)

    #         if number == self.count + 1:
    #             self.count = number

    #             if self.count in [10, 100, 500, 1000, 5000, 100000]:
    #                 await message.pin()
    #         else:
    #             await message.delete()
    #             msg=await message.channel.send(f"That is not the correct next number.")
    #             asyncio.sleep(1)
    #             await msg.delete()
    #     else:
    #         await message.delete()
    #         msg = await message.channel.send(f"Your message must be a number.")
    #         asyncio.sleep(1)
    #         await msg.delete()

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Fun(bot))
