import asyncio
import textwrap

import aiosqlite
import discord
from discord import ui
from discord.ext import commands

from config import DB



class Messages(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

@commands.Cog.listener()
async def on_message(self, message):
    pass

async def setup(bot: commands.Bot):
    await bot.add_cog(Messages(bot))