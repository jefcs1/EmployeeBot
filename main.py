import asyncio
import logging
import os
import random
import sys
from typing import Literal, Optional

import discord
from discord.ext import commands, tasks

from config import test_token, token

TESTING = sys.platform == "darwin"
TOKEN = token if not TESTING else test_token
PREFIX = "!" if not TESTING else "t!"

class MyBot(commands.Bot):
    async def setup_hook(self):
        change_status.start()
        print(
        f"Logged in as {bot.user}\n----------------------------------------------------"
        )

bot = MyBot(
    command_prefix=PREFIX,
    intents=discord.Intents.all(),
    help_command=None,
    status=discord.Status.online,
    )

custom_statuses = [
    "Don't log into unknown sites!",
    "Beware of impersonators!",
    "Stay safe from Scams!",
    "Banning Peter...",
]

@tasks.loop(minutes=10)
async def change_status():
    new_status = random.choice(custom_statuses)
    await bot.change_presence(activity=discord.CustomActivity(name=new_status))

@change_status.before_loop
async def before_status():
    await bot.wait_until_ready()

handler = logging.FileHandler(
    filename="logs/EmployeeBot.log", encoding="utf-8", mode="w"
)
discord.utils.setup_logging(handler=handler)
logger = logging.getLogger("EmployeeBot")



# get the extensions
async def get_extensions() -> list[str]:
    extensions = []
    for root, _, files in os.walk("extensions"):
        extensions.extend(
            os.path.join(root, file[:-3]).replace("/", ".")
            for file in files
            if file.endswith(".py")
        )
    return extensions


# load the extension
async def mass_load() -> None:
    await bot.load_extension("jishaku")
    if not (os.listdir("./extensions")):
        logger.critical("No extensions Directory To Load!")
        return
    for extension in await get_extensions():
        try:
            await bot.load_extension(extension)
            logger.info(f"Loaded {extension}")
        except Exception as e:
            logger.exception(e)


# create the bot tree
@bot.command()
@commands.guild_only()
@commands.is_owner()
async def sync(
    ctx: commands.Context,
    guilds: commands.Greedy[discord.Object],
    spec: Optional[Literal["~", "*", "^"]] = None,
) -> None:
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild) 
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")


async def main() -> None:
    async with bot:
        await mass_load()
        print(await get_extensions())
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
