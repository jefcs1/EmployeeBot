import datetime
import logging
import random

import aiosqlite
import arrow
import discord
from discord import app_commands
from discord.ext import commands, tasks

from config import DB


async def roll(reaction, traders_compound_guild):
    role_entries = {
        "Level 20": 1,
        "Level 40": 1,
        "Level 60": 1,
        "Level 80": 1,
        "Level 100": 1,
        "Classified": 1,
        "Covert": 2,
        "Contraband": 4,
    }

    users = [u async for u in reaction.users() if not u.bot]

    extra_entries_users = []
    for role_name, extra_entries in role_entries.items():
        role = discord.utils.get(traders_compound_guild.roles, name=role_name)
        if role:
            role_users = [u for u in users if role in u.roles]
            extra_entries_users.extend(role_users * extra_entries)

    users += extra_entries_users

    if users:
        winner = random.choice(users)

    return winner


async def flag(message_id, channel_id):
    async with aiosqlite.connect(DB) as conn:
        cursor = await conn.cursor()
        await cursor.execute(
            "UPDATE Giveaways SET completed = TRUE WHERE message_id = ? AND channel_id = ?",
            (message_id, channel_id),
        )
        await conn.commit()


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


class Giveaway(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.logger = logging.getLogger(f"EmployeeBot.{self.__class__.__name__}")
        self.bot = bot

    def cog_load(self) -> None:
        self.giveaway.start()

    def cog_unload(self) -> None:
        self.giveaway.cancel()

    @app_commands.command(name="giveawaycreate", description="Create a Giveaway")
    @app_commands.describe(prize="Seperate items with a comma")
    @app_commands.describe(duration="How long should the giveaway last")
    @app_commands.describe(channel="The channel this giveaway should be sent in")
    async def slash_giveawaycreate(
        self,
        interaction: discord.Interaction,
        prize: str,
        duration: str,
        channel: discord.TextChannel,
    ):
        time = convert(duration)
        if time == -1:
            await interaction.response.send_message(
                f"You didn't use a proper unit when specifying the duration.Please use (s|m|h|d)"
            )
            return
        elif time == -2:
            await interaction.response.send_message(
                f"The time must be an integer, please use an integer next time."
            )
            return

        channel_id = channel.id

        end_time = discord.utils.utcnow() + datetime.timedelta(seconds=time)
        end_time_relative = discord.utils.format_dt(end_time, "R")

        GiveawayEmbed = discord.Embed(title=f"{prize}", description="ㅤ", color=0x86DEF2)
        GiveawayEmbed.add_field(
            name=f"<:tc_clock:1126623703996838018> Ends: {end_time_relative}",
            value="ㅤ",
            inline=False,
        )
        GiveawayEmbed.add_field(
            name="<:tc_plus:1126625934607400980> Extra Luck:",
            value="• <@&1121860722054414397> 2-5 Extra Entries\n• Every 20 levels you get an extra entry",
            inline=False,
        )
        GiveawayEmbed.set_footer(text="React below to enter")

        await interaction.response.send_message(
            "Giveaway successfully created!", ephemeral=True
        )
        msg = await channel.send(embed=GiveawayEmbed)
        await msg.add_reaction("<:tc_tada:1102929530794016870>")

        async with aiosqlite.connect(DB) as conn:
            cursor = await conn.cursor()
            await cursor.execute(
                """INSERT INTO Giveaways (prize, end_time, channel_id, message_id) VALUES (?, ?, ?, ?)""",
                (prize, end_time, channel_id, msg.id),
            )
            await conn.commit()

        if self.giveaway.is_running():
            self.giveaway.restart()
        else:
            self.giveaway.start()

    @tasks.loop()
    async def giveaway(self):
        async with aiosqlite.connect(DB) as conn:
            cursor = await conn.cursor()
            await cursor.execute(
                "SELECT prize, end_time, completed, channel_id, message_id FROM Giveaways WHERE completed = FALSE ORDER BY datetime(end_time) ASC LIMIT 1"
            )
            row = await cursor.fetchone()

        if not row:
            self.giveaway.stop()
            return

        prize, end_time, completed, channel_id, message_id = row

        channel = self.bot.get_channel(channel_id)

        end_time_dt = datetime.datetime.fromisoformat(end_time)

        await discord.utils.sleep_until(end_time_dt)

        channel = self.bot.get_channel(channel_id)
        if not channel:
            print("The specified channel was not found.")
            flag(message_id, channel_id)
            return

        m = await channel.fetch_message(message_id)
        if not m:
            await channel.send("The specified message was not found.")
            flag(message_id, channel_id)
            return

        traders_compound_guild = self.bot.get_guild(953632089339727953)
        custom_emoji = discord.utils.get(traders_compound_guild.emojis, name="tc_tada")
        reaction = discord.utils.get(m.reactions, emoji=custom_emoji)

        if not reaction:
            await channel.send("The specified reaction was not found.")
            flag(message_id, channel_id)
            return

        winner = await roll(reaction, traders_compound_guild)

        await channel.send(
            f"Congratulations {winner.mention}, you won the {prize}! <:tc_tada:1102929530794016870>"
        )

        FinishedEmbed = discord.Embed(
            title=f"{prize}", description="This Giveaway Has Ended", color=0x86DEF2
        )
        FinishedEmbed.add_field(name=f"", value=f"The winner was {winner.mention}")
        await m.edit(embed=FinishedEmbed)

        async with aiosqlite.connect(DB) as conn:
            cursor = await conn.cursor()
            await cursor.execute(
                "UPDATE Giveaways SET completed = TRUE WHERE channel_id = ? AND message_id = ?",
                (channel_id, message_id),
            )
            await conn.commit()

    @app_commands.command(
        name="giveawayreroll", description="Rerolls the winner of a specified giveaway"
    )
    @app_commands.describe(message_id="The developer ID of the giveaway message")
    @app_commands.describe(channel_id="The developer ID of the giveaway's channel")
    async def slash_giveawayreroll(
        self, interaction: discord.Interaction, message_id: str, channel_id: str
    ):
        async with aiosqlite.connect(DB) as conn:
            cursor = await conn.cursor()
            await cursor.execute(
                "SELECT prize FROM Giveaways WHERE message_id = ? AND channel_id = ?",
                (message_id, channel_id),
            )
            row = await cursor.fetchone()

        if not row:
            return

        prize = row[0]

        channel = self.bot.get_channel(int(channel_id))
        if not channel:
            print("The specified channel was not found.")
            flag(message_id, channel_id)
            return

        m = await channel.fetch_message(int(message_id))
        if not m:
            await channel.send("The specified message was not found.")
            flag(message_id, channel_id)
            return

        traders_compound_guild = self.bot.get_guild(953632089339727953)
        custom_emoji = discord.utils.get(traders_compound_guild.emojis, name="tc_tada")
        reaction = discord.utils.get(m.reactions, emoji=custom_emoji)

        if not reaction:
            await channel.send("The specified reaction was not found.")
            flag(message_id, channel_id)
            return

        winner = await roll(reaction, traders_compound_guild)

        await interaction.response.send_message("New Winner Successfully Picked!")
        await channel.send(
            f"Congratulations {winner.mention}, you are the new winner! <:tc_tada:1102929530794016870>"
        )

        FinishedEmbed = discord.Embed(
            title=f"{prize}", description="This Giveaway Has Ended", color=0x86DEF2
        )
        FinishedEmbed.add_field(name=f"", value=f"The winner was {winner.mention}")
        await m.edit(embed=FinishedEmbed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Giveaway(bot))
