import datetime
import logging
import random

import aiosqlite
import discord
from discord import app_commands
from discord.ext import commands, tasks

from config import DB

ROLE_ENTRIES = {
    "Level 20": 1,
    "Level 40": 1,
    "Level 60": 1,
    "Level 80": 1,
    "Level 100": 1,
    "Level 120": 1,
    "Level 140": 1,
    "Patreon ━ Tier 1": 1,
    "Patreon ━ Tier 2": 2,
    "Patreon ━ Tier 3": 5,
}


def get_member_entires(member: discord.Member) -> list[discord.Member]:
    """Returns a list of the given Member denoting their number of entries."""
    g = member.guild

    get_role_named = lambda rn: discord.utils.get(g.roles, name=rn)

    ret = [member]

    for role_name, num_entries in ROLE_ENTRIES.items():
        role = get_role_named(role_name)

        if not role:
            continue

        if role in member.roles:
            ret.extend([member] * num_entries)

    return ret


async def roll(
    message_id: int, channel_id: int, tc_guild: discord.Guild
) -> discord.Member:
    async with aiosqlite.connect(DB) as conn:
        cursor = await conn.cursor()
        await cursor.execute(
            "SELECT id FROM Giveaways WHERE message_id = ? AND channel_id = ?",
            (message_id, channel_id),
        )
        giveaway_id = await cursor.fetchone()

        if giveaway_id:
            await cursor.execute(
                "SELECT user_id FROM GiveawayEntries WHERE giveaway_id = ?",
                (giveaway_id[0],),
            )

            user_ids = await cursor.fetchall()

        if not user_ids:
            return

        all_entries = []

        for id_ in user_ids:
            mem = tc_guild.get_member(id_[0])

            if not mem:
                continue

            member_entries = get_member_entires(mem)
            all_entries.append(member_entries)

        winner_list = random.choice(all_entries)
        winner_element = winner_list[0]
        return winner_element


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


class PersistentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="0",
        style=discord.ButtonStyle.green,
        custom_id="persistent_view:giveaway",
        emoji="<:tc_tada:1102929530794016870>",
    )
    async def giveaway_enter(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        async with aiosqlite.connect(DB) as conn:
            cursor = await conn.cursor()
            await cursor.execute(
                """SELECT user_id FROM giveawayentries 
                WHERE giveaway_id = (SELECT id FROM giveaways WHERE message_id = ? AND channel_id = ?) 
                AND user_id = ?""",
                (interaction.message.id, interaction.channel.id, interaction.user.id),
            )
            existing_entry = await cursor.fetchone()

            if existing_entry:
                await interaction.response.send_message(
                    "You are already entered into this giveaway.", ephemeral=True
                )
                await conn.commit()
            else:
                await cursor.execute(
                    """WITH gwtab AS (SELECT id FROM giveaways WHERE message_id = ? AND channel_id = ?)
                    INSERT INTO giveawayentries (user_id, giveaway_id) VALUES (?, (SELECT id FROM gwtab))
                    RETURNING (SELECT count(*) AS num_entries FROM giveawayentries WHERE giveaway_id = (SELECT id FROM gwtab))""",
                    (
                        interaction.message.id,
                        interaction.channel.id,
                        interaction.user.id,
                    ),
                )

                row = await cursor.fetchone()
                await conn.commit()

                confirmationEmbed = discord.Embed(
                    title="Entry Confirmed",
                    timestamp=datetime.datetime.now(),
                    description=f"You were successfully entered into the giveaway.",
                    color=0x86DEF2,
                )
                confirmationEmbed.add_field(
                    name="Good Luck! <:HeartTC:1102665571872555099>", value=""
                )

                button.label = f"{row[0]}"
                original_embed = interaction.message.embeds[0]

                await interaction.response.edit_message(embed=original_embed, view=self)

                await interaction.followup.send(embed=confirmationEmbed, ephemeral=True)


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
            value="• <@&1121931624670580908> 1 Extra Entry\n• <@&1121860931861893190> 2 Extra Entries\n• <@&1121860948370673747> 5 Extra Entries\n• Every 20 levels you get an extra entry",
            inline=False,
        )
        GiveawayEmbed.set_footer(text="Click the button below to enter")

        await interaction.response.send_message(
            "Giveaway successfully created!", ephemeral=True
        )

        msg = await channel.send(embed=GiveawayEmbed, view=PersistentView())

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
            await conn.commit()

        if not row:
            self.giveaway.stop()
            return

        prize, end_time, completed, channel_id, message_id = row

        tc_guild_id = 953632089339727953
        tc_guild = self.bot.get_guild(tc_guild_id)

        channel = self.bot.get_channel(channel_id)
        if not channel:
            print("The specified channel was not found.")
            flag(message_id, channel_id)
            return

        end_time_dt = datetime.datetime.fromisoformat(end_time).replace(
            tzinfo=datetime.timezone.utc
        )

        await discord.utils.sleep_until(end_time_dt)

        m = await channel.fetch_message(message_id)
        if not m:
            await channel.send("The specified message was not found.")
            flag(message_id, channel_id)
            return

        winner = await roll(message_id, channel_id, tc_guild)

        await channel.send(
            f"Congratulations {winner.mention}, you won the {prize}! <:tc_tada:1102929530794016870>"
        )

        FinishedEmbed = discord.Embed(
            title=f"{prize}", description="This Giveaway Has Ended", color=0x86DEF2
        )
        FinishedEmbed.add_field(name=f"", value=f"The winner was {winner.mention}")
        await m.edit(embed=FinishedEmbed, view=None)

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

        tc_guild_id = 953632089339727953
        tc_guild = self.bot.get_guild(tc_guild_id)

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

        new_winner = await roll(message_id, channel_id, tc_guild)

        await interaction.response.send_message(
            "New Winner Successfully Picked!", ephemeral=True
        )
        await channel.send(
            f"Congratulations {new_winner.mention}, you are the new winner! <:tc_tada:1102929530794016870>"
        )

        FinishedEmbed = discord.Embed(
            title=f"{prize}", description="This Giveaway Has Ended", color=0x86DEF2
        )
        FinishedEmbed.add_field(name=f"", value=f"The winner was {new_winner.mention}")
        await m.edit(embed=FinishedEmbed)

    @giveaway.before_loop
    async def before_giveaway_loop(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Giveaway(bot))
