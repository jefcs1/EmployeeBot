import datetime
import logging
from datetime import date

import aiosqlite
import discord
from discord import app_commands
from discord.ext import commands, tasks

from config import DB

LOW_TIER_ID = 957348847175209030
MID_TIER_ID = 953632090149232731
HIGH_TIER_ID = 957349993847615489


class AutoPost(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.logger = logging.getLogger(f"EmployeeBot.{self.__class__.__name__}")
        self.bot = bot

    @app_commands.command(
        name="createautopost", description="Create an automatic trade advertisement!"
    )
    @app_commands.describe(have="Seperate items with a comma")
    @app_commands.describe(want="Seperate items with a comma")
    @app_commands.describe(tradelink="Add your working tradelink")
    @app_commands.describe(channel="The ID of the channel this should post in")
    async def slash_createautopost(
        self,
        interaction: discord.Interaction,
        have: str,
        want: str,
        tradelink: str,
        channel: discord.TextChannel,
    ):
        await interaction.response.defer(ephemeral=True)

        channel_id = channel.id
        CONTRABAND_ROLE_ID = 1121860948370673747

        if not interaction.user.get_role(CONTRABAND_ROLE_ID):
            infoEmbed = discord.Embed(
                title="You don't have access to this command.",
                description="This is a feature that lets traders auto their trade advertisements.\nTo get access to this yourself, check out #patreon.",
                color=0x313338,
            )
            await interaction.followup.send(embed=infoEmbed, ephemeral=True)
            return

        if not channel_id in (LOW_TIER_ID, MID_TIER_ID, HIGH_TIER_ID):
            await interaction.followup.send(
                "Invalid channel selection. Please select a valid channel.",
                ephemeral=True,
            )
            return

        async with aiosqlite.connect(DB) as conn:
            cursor = await conn.cursor()

            await cursor.execute(
                """INSERT INTO TradeAds (have, want, tradelink, channel_id, user_id) VALUES (?, ?, ?, ?, ?)
                                ON CONFLICT (user_id, channel_id) DO
                                UPDATE SET have = excluded.have, want = excluded.want, tradelink = excluded.tradelink, next_post = datetime(CURRENT_TIMESTAMP, '+3 hours')""",
                (have, want, tradelink, channel_id, interaction.user.id),
            )
            await conn.commit()

        await interaction.followup.send(
            "Trade information stored and scheduled for autoposting!", ephemeral=True
        )

        if self.posttask.is_running():
            self.posttask.restart()
        else:
            self.posttask.start()

    @tasks.loop()
    async def posttask(self):
        async with aiosqlite.connect(DB) as conn:
            cursor = await conn.cursor()
            await cursor.execute(
                "SELECT have, want, tradelink, channel_id, user_id, next_post FROM TradeAds ORDER BY datetime(next_post) ASC LIMIT 1"
            )
            row = await cursor.fetchone()

        if not row:
            self.posttask.stop()
            return
        have, want, tradelink, channel_id, user_id, next_post = row

        next_post_dt = datetime.datetime.fromisoformat(next_post)

        next_post_datetime = next_post_dt.replace(tzinfo=datetime.timezone.utc)

        print(next_post_datetime)

        await discord.utils.sleep_until(next_post_datetime)

        have_items = have.split(",")
        want_items = want.split(",")

        author = await self.bot.fetch_user(user_id)
        avatar_bytes = await author.avatar.read()
        avatar_url = author.avatar.url

        ad_channel = self.bot.get_channel(channel_id)

        webhooks = await ad_channel.webhooks()

        bot_webhook = discord.utils.get(
            webhooks, user__id=self.bot.user.id
        ) or await ad_channel.create_webhook(name=author.name, avatar=avatar_bytes)

        trade_message = f"**{author.name}'s Trade Advertisement**\n\n"
        trade_message += f"**[Have]**\n"
        for item in have_items:
            trade_message += f"- {item.strip()}\n"
        trade_message += f"\n"
        trade_message += f"**[Want]**\n"
        for item in want_items:
            trade_message += f"- {item.strip()}\n"
        trade_message += f"\n"
        trade_message += f"**[Trade Link]**\n{tradelink.strip()}"

        line = "<:tcline:1121511395612180631>" * 27

        infoEmbed = discord.Embed(
            title="What is this?",
            description="This is a feature that lets traders autopost their trade advertisements\nand not have to wait the entire 6-hour cooldown\nTo get access to this yourself, check out #patreon.",
            color=0x313338,
        )

        await bot_webhook.send(
            content=f"{line}\n{trade_message}",
            embed=infoEmbed,
            username=author.name,
            avatar_url=avatar_url,
        )

        async with aiosqlite.connect(DB) as conn:
            cursor = await conn.cursor()

            await cursor.execute(
                "UPDATE TradeAds SET next_post = datetime(next_post, '+3 hours') WHERE user_id = ? AND channel_id = ?",
                (user_id, channel_id),
            )
            (user_id, channel_id)

            await conn.commit()

    @posttask.before_loop
    async def before_posttask(self):
        print("waiting to start...")
        await self.bot.wait_until_ready()

    @app_commands.command(name="cleartdb", description="Clear the trade database")
    @app_commands.default_permissions(administrator=True)
    async def slash_cleartdb(self, interaction: discord.Interaction):
        await interaction.response.defer()
        async with aiosqlite.connect(DB) as conn:
            cursor = await conn.cursor()
            await cursor.execute("DELETE FROM TradeAds")
            await conn.commit()
        await interaction.followup.send("Trade database cleared.")

    @app_commands.command(
        name="stopauto", description="Stops the autoposting across the entire server"
    )
    @app_commands.default_permissions(administrator=True)
    async def slash_stopauto(self, interaction: discord.Interaction):
        if interaction.user.guild_permissions.administrator:
            await interaction.response.defer()
            self.posttask.stop()
            await interaction.followup.send("Serverwide autoposting has been stopped.")
        else:
            await interaction.response.send_message(
                "You don't have permission to run this command"
            )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AutoPost(bot))
