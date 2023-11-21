import asyncio
import textwrap

import aiosqlite
import discord
from discord import ui
from discord.ext import commands

from config import DB

SUBMISSIONS_FORUM_ID = 1173037697821069402
MAX_FILE_SIZE = 1024 * 1024 * 32  # 32 MiB
EMBED_COLOR = 0x86DEF2

SUBMISSION_TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS loadout_event_entries (
    user_id INTEGER NOT NULL PRIMARY KEY,
    submitted INTEGER NOT NULL DEFAULT 1
);
"""

async def has_submitted(user_id: int, db_filename: str = DB) -> bool:
    async with aiosqlite.connect(db_filename) as conn:
        cur = await conn.execute(
            "SELECT submitted FROM loadout_event_entries WHERE user_id = ?",
            (user_id,),
        )

        res = await cur.fetchone()

        return False if not res else bool(res[0])


async def mark_submitted(
    user_id: int, submitted: bool = True, db_filename: str = DB
):
    async with aiosqlite.connect(db_filename) as conn:
        await conn.execute(
            "INSERT INTO loadout_event_entries (user_id, submitted) VALUES (?, ?) ON CONFLICT DO UPDATE SET submitted = excluded.submitted",
            (user_id, submitted),
        )
        await conn.commit()


class EventView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(
        label="Participation Instructions", custom_id="11-2023-loadout-event-button"
    )
    async def participate_button(self, interaction: discord.Interaction, _: ui.Button):
        # Sends embed with info about the event, what the user will need to have ready, when it ends, etc.
        description = """
        ### You will need:
        - A description of your loadout.
        - Images of your loadout. You may have up to 10. Each image must be under 32MB to be submitted.

        ### How to submit
        Start a DM with the TC Employee and use the `!submit` command to get started, the bot will prompt you for your submission information.
        """
        embed = discord.Embed(
            title="Loadout Event!",
            description=textwrap.dedent(description),
            color=EMBED_COLOR,
        )
        embed.set_footer(text="Thank you for participating!")

        await interaction.response.send_message(embed=embed, ephemeral=True)


class LoadoutEventCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def cog_load(self) -> None:
        async with aiosqlite.connect(DB) as conn:
            await conn.executescript(SUBMISSION_TABLE_SCHEMA)
            await conn.commit()

        self.bot.add_view(EventView())

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def loadoutview(self, ctx: commands.Context):
        """Sends the participation instructions embed."""
        await ctx.send(view=EventView())

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def resetentry(
        self, ctx: commands.Context, user: discord.Member | discord.User
    ):
        """Allow the given user to enter the event again."""
        await mark_submitted(user.id, False)
        await ctx.send(f"Success, {user} can submit again.")

    @commands.command()
    @commands.dm_only()
    async def submit(self, ctx: commands.Context):
        """Allows you to interactively enter the loadout event."""

        if await has_submitted(ctx.author.id):
            return await ctx.send(
                "You've already entered the event. If you want to redo your submission, please let an admin know."
            )

        # A lil sanity checking first.
        submissions_channel: discord.ForumChannel = self.bot.get_channel(SUBMISSIONS_FORUM_ID)  # type: ignore

        if not submissions_channel:
            return await ctx.send(
                "Something has gone catastrophically wrong, please let fretgfr or jef know."
            )

        # check for msg waiting.
        def check(m: discord.Message):
            return m.guild is None and m.author.id == ctx.author.id

        # Gather info
        await ctx.send("Lets get started. What is the description for your post?")

        description_msg = await self.bot.wait_for("message", check=check, timeout=360.0)

        description = description_msg.content

        if not description:
            return await ctx.send(
                "I didn't see anything in your description, please start over."
            )

        await ctx.send(
            "Got it, what images do you want to upload with it? "
            "You can give up to 10 images. Each image must be 32MB or smaller to be submitted."
        )

        files_message = await self.bot.wait_for("message", check=check, timeout=360.0)

        if not files_message.attachments:
            return await ctx.send(
                "I don't see any attachements, please start over again."
            )

        files = [
            await a.to_file()
            for a in files_message.attachments
            if a.size <= MAX_FILE_SIZE
        ]

        await ctx.send("Got it, let me make the submission thread now.")

        # Create thread.
        thread_name = f"{ctx.author.name} ({ctx.author.id})"
        thread, _ = await submissions_channel.create_thread(
            name=thread_name, content=description, files=files
        )

        # Send success message.
        success_title = "Thread Created"
        success_description = (
            f"### Thank you for entering the event, your submission has been successfully received and posted.\n\n"
            f"Your thread is located [HERE]({thread.jump_url})"
        )

        success_embed = discord.Embed(
            title=success_title, description=success_description, color=EMBED_COLOR
        )

        await ctx.send(embed=success_embed)

        await mark_submitted(ctx.author.id)

    @submit.error
    async def on_submit_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        err = getattr(error, "original", error)

        if isinstance(err, asyncio.TimeoutError):
            await ctx.send(
                "Submission cancelled, please use the command again to start over."
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(LoadoutEventCog(bot))
