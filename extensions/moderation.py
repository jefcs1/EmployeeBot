import logging
import datetime
import discord  # type: ignore
from discord import app_commands
import asyncio
from datetime import timedelta
from discord.ext import commands, tasks


def convert(time):
    pos = ["s", "m", "h", "d"]

    time_dict = {"s": 1, "m": 60, "h": 3600, "d": 3600 * 24}

    unit = time[-1]
    if unit not in pos:
        return -1
    try:
        val = int(time[:-1])
    except:
        return -2

    return val * time_dict[unit]


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.logger = logging.getLogger(f"EmployeeBot.{self.__class__.__name__}")

    @discord.ext.commands.hybrid_command(name="mute", description="Mutes a user")
    @app_commands.describe(user="The user that you want to mute")
    @app_commands.describe(mute_time="The amount of time you want to mute them for")
    @app_commands.describe(mute_reason="Your reason for muting them")
    async def slash_mute(
        self,
        ctx,
        user: discord.Member,
        mute_time: str = "None",
        mute_reason: str = "None",
    ):
        if mute_time == "None":
            mute_time = "28d"

        time = convert(mute_time)
        if time == -1:
            await ctx.send(
                f"You didn't use a proper unit when specifying the duration. Please use (s|m|h|d)"
            )
            return
        elif time == -2:
            await ctx.send(
                f"The time must be an integer, please use an integer next time."
            )
            return
        else:
            if time > 28 * 24 * 60 * 60:
                await ctx.send("Timeout duration cannot exceed 28 days.")
                return
            mute_until = discord.utils.utcnow() + timedelta(seconds=time)
            await user.timeout(mute_until, reason=mute_reason)
            msg = await ctx.send(f"Sucessfully muted {user.mention}.")
            await asyncio.sleep(2)
            await msg.delete()

    @discord.ext.commands.hybrid_command(name="unmute", description="Unmutes a user")
    @app_commands.describe(user="The user that you want to unmute")
    @app_commands.describe(unmute_reason="Your reason for unmuting them")
    async def slash_unmute(
        self, ctx, user: discord.Member, unmute_reason: str = "None"
    ):
        await user.timeout(None, reason=unmute_reason)
        msg = await ctx.send(f"Sucessfully unmuted {user.mention}.")
        await asyncio.sleep(2)
        await msg.delete()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Moderation(bot))
