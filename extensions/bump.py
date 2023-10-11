import datetime
import logging

import aiosqlite
import discord
from discord import app_commands
from discord.ext import commands, tasks
from PIL import Image, ImageDraw, ImageFont

from config import DB, DISBOARD_BOT_ID


def add_line(img, start_point, end_point, color=(255, 255, 255), thickness=1):
    draw = ImageDraw.Draw(img)
    draw.line([start_point, end_point], fill=color, width=thickness)


class Bump(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.logger = logging.getLogger(f"EmployeeBot.{self.__class__.__name__}")
        self.bot = bot
        self.next_bump_dt = None

    def has_embed_and_description(self, msg: discord.Message) -> bool:
        return bool(msg.embeds) and msg.embeds[0].description is not None

    def is_bump_interaction(self, msg: discord.Message) -> bool:
        return msg.interaction is not None and msg.interaction.name == "bump"

    def is_bump_message(self, msg: discord.Message) -> bool:
        return (
            msg.author.id == DISBOARD_BOT_ID
            and self.is_bump_interaction(msg)
            and self.has_embed_and_description(msg)
        )

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        channel = msg.channel

        if not msg.guild:
            return

        if not self.is_bump_message(msg):
            return

        if not msg.interaction:
            return

        async with aiosqlite.connect(DB) as conn:
            cursor = await conn.cursor()
            await cursor.execute(
                """INSERT INTO Bumps (guild_id, channel_id, user_id) VALUES (?, ?, ?)""",
                (msg.guild.id, msg.channel.id, msg.interaction.user.id),
            )
            await conn.commit()

        await channel.send(f"Bump recorded for {msg.interaction.user.display_name}")

        two_hours_future = discord.utils.utcnow() + datetime.timedelta(hours=2)
        self.next_bump_dt = two_hours_future

        await discord.utils.sleep_until(two_hours_future)

        embed = discord.Embed(
            title="Bump is available again!",
            description="Please type `/bump` again!",
            color=0x86DEF2,
        )
        embed.add_field(
            name=" Bumping will help us stay at the top of the Counter-Strike Tags on Disboard, so that more people can find our server!.",
            value="Thank you so much for your help <:HeartTC:1102665571872555099>",
        )

        await channel.send(embed=embed)

    @app_commands.command(name="bumps", description="Shows you the 5 most recent bumps")
    async def slash_bumps(self, interaction: discord.Interaction):
        async with aiosqlite.connect(DB) as conn:
            cursor = await conn.cursor()
            await cursor.execute(
                "SELECT * FROM Bumps WHERE guild_id = ? ORDER BY timestamp DESC LIMIT 5",
                (interaction.guild.id,),
            )
            bumps = await cursor.fetchall()

        if not bumps:
            return await interaction.response.send_message(
                "No bumps have been recorded"
            )

        embed = discord.Embed(title="Recent Bumps", color=0x86DEF2)
        for bump in bumps:
            bumper = interaction.guild.get_member(bump[3])
            bumper_str = bumper.display_name if bumper else str(bump[3])

            timestamp = datetime.datetime.fromisoformat(bump[4]).replace(
                tzinfo=datetime.timezone.utc
            )

            embed.add_field(
                name=bumper_str, value=discord.utils.format_dt(timestamp), inline=False
            )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="leaderboardbumps",
        description="Shows the users with the top amount of bumps",
    )
    async def slash_leaderboardbumps(self, interaction: discord.Interaction):
        await interaction.response.defer()

        img = Image.open("images/bumpbackground.png")

        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("images/fonts/Montserrat-Bold.ttf", 150)

        async with aiosqlite.connect(DB) as conn:
            cursor = await conn.cursor()
            await cursor.execute(
                "SELECT user_id, count(*) as num FROM bumps WHERE guild_id = ? GROUP BY user_id ORDER BY num DESC LIMIT 3",
                (interaction.guild.id,),
            )
            row = await cursor.fetchall()

        if not row:
            await interaction.followup.send("No data recorded for this guild.")
            return

        text = ""
        top_bumpers = row
        for i, row in enumerate(top_bumpers, 1):
            user_id, num_bumps = row

            user = self.bot.fetch_user(user_id)
            text += f"{user} - {num_bumps}\n\n"

        draw.text((445, 490), text, (255, 255, 255), font=font)

        img.save("bump.png")

        await interaction.followup.send(file=discord.File("bump.png"))

    @app_commands.command(
        name="nextbump", description="Tells you when the next bump is"
    )
    async def slash_nextbump(self, interaction: discord.Interaction):
        if not self.next_bump_dt:
            return await interaction.response.send_message(
                "Haven't seen a previous bump"
            )

        await interaction.response.send_message(
            f"{discord.utils.format_dt(self.next_bump_dt)}"
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Bump(bot))
