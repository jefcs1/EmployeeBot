import asyncio
import datetime
import logging
import sys
import typing
from datetime import datetime, timedelta

import aiosqlite
import arrow
import discord  # type: ignore
from discord import app_commands
from discord.ext import commands, tasks

from config import (DB, admin_chat_id, admin_id, console_id, founder_id,
                    manager_id, mod_logs_id, moderator_id, server_staff_id,
                    support_id, trial_mod_id, counting_id)


def convert(time):
    time_dict = {"s": 1, "m": 60, "h": 3600, "d": 3600 * 24}

    unit = time[-1]
    val = int(time[:-1])

    return val * time_dict[unit]


class WarningView(discord.ui.View):
    def __init__(self, info, user, author_id):
        super().__init__(timeout=None)
        self.info = info
        self.user = user
        self.author_id = author_id

    @discord.ui.button(
        label="Delete a warning",
        style=discord.ButtonStyle.red,
        emoji="🗑️",
    )
    async def delete_warnings(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message("This button is not for you", ephemeral=True)
        embed = discord.Embed(
            title=f"{len(self.info)} Warning(s) for {self.user.display_name} ({self.user.id})",
            description="Select one to delete",
            color=0x86DEF2,
        )
        await interaction.response.send_message(
            embed=embed, view=DropdownView(self.info, self.user), ephemeral=True
        )


class DropdownView(discord.ui.View):
    def __init__(self, info, user):
        super().__init__(timeout=None)
        self.add_item(WarningsDropdown(info, user))


class WarningsDropdown(discord.ui.Select):
    def __init__(self, info, user):
        self.info = info
        self.user = user

        options = []
        for row in self.info:
            date_string = row[2]
            dt = arrow.get(date_string)
            options.append(
                discord.SelectOption(
                    label=f"{row[1]} - {dt}", value=f"{row[3]}, {self.user.id}"
                )
            )

        super().__init__(
            placeholder="Select a warning to delete",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        print(interaction.data)
        split_list = interaction.data["values"][0].split(", ")
        print(split_list)
        selected_id = split_list[0]
        selected_user_id = split_list[1]

        async with aiosqlite.connect(DB) as conn:
            cursor = await conn.cursor()
            await cursor.execute(
                """DELETE FROM Warns WHERE user_id = ? AND warn_id = ?""",
                (selected_user_id, selected_id),
            )
            await conn.commit()
        await interaction.response.send_message(
            content="Sucessfully deleted that warning", ephemeral=True
        )


class PunishTime(commands.Converter):
    async def convert(self, ctx, argument):
        time = convert(argument)
        return time


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.logger = logging.getLogger(f"EmployeeBot.{self.__class__.__name__}")

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.MissingAnyRole):
            await ctx.send("You do not have permission to use this command.")

    async def cog_load(self) -> None:
        self.tempban.start()

    def cog_unload(self) -> None:
        self.tempban.cancel()

    # WARN COMMAND

    @discord.ext.commands.hybrid_command(name="warn", description="Warns a user")
    @commands.has_any_role(
        founder_id,
        manager_id,
        admin_id,
        moderator_id,
        trial_mod_id,
        server_staff_id,
        support_id,
    )
    @app_commands.describe(user="The user that you want to warn")
    @app_commands.describe(reason="The reason for warning them")
    async def slash_warn(
        self,
        ctx,
        user: discord.User,
        *,
        reason: typing.Optional[str] = "No reason provided",
    ):
        tc_obj = self.bot.get_guild(953632089339727953)
        mem_id = user.id
        member = await tc_obj.fetch_member(mem_id)

        if ctx.author.top_role <= member.top_role:
            await ctx.send(
                "You can't warn someone with a role equal or higher than yours."
            )
            return

        if user == self.bot.user or user == ctx.author:
            await ctx.send("You cannot warn this user.")
            return

        async with aiosqlite.connect(DB) as conn:
            cursor = await conn.cursor()
            await cursor.execute(
                """INSERT INTO Warns (moderator_id, user_id, warn_reason) VALUES (?, ?, ?)""",
                (ctx.author.id, user.id, reason),
            )
            await conn.commit()

        dmEmbed = discord.Embed(
            title="You were warned in Traders Compound!",
            description="",
            color=0x86DEF2,
        )
        dmEmbed.set_author(
            name="Traders Compound Moderation", icon_url=ctx.guild.icon.url
        )
        dmEmbed.add_field(name="You were warned for the reason:", value=f'"{reason}"')
        await member.send(embed=dmEmbed)
        warnE = discord.Embed(
            title="", description=f"Sucessfully warned {member.mention}", color=0x86DEF2
        )
        log_embed = discord.Embed(
            title="", description="", color=0xFF0000, timestamp=datetime.now()
        )
        log_embed.set_author(name=f"Warn | {user.display_name}", icon_url=user.avatar)
        log_embed.add_field(name="User", value=f"{user.mention}")
        log_embed.add_field(name="Moderator", value=f"{ctx.author.mention}")
        log_embed.add_field(name="Reason", value=f"{reason}")
        log_embed.set_footer(text=f"ID: {user.id}")
        await ctx.message.delete()
        msg = await ctx.send(embed=warnE)
        c = self.bot.get_channel(mod_logs_id)
        await c.send(embed=log_embed)
        await asyncio.sleep(5)
        await msg.delete()

    @discord.ext.commands.hybrid_command(
        name="warnings", description="View a user's warnings"
    )
    @commands.has_any_role(
        founder_id,
        manager_id,
        admin_id,
        moderator_id,
        trial_mod_id,
        server_staff_id,
        support_id,
    )
    @app_commands.describe(user="The user that you want to view the warnings for")
    async def slash_warnings(self, ctx, user: discord.User):
        if user is None:
            await ctx.send("You must provide a user to view the warnings of")
        async with aiosqlite.connect(DB) as conn:
            cursor = await conn.cursor()
            await cursor.execute(
                "SELECT moderator_id, warn_reason, timestamp, warn_id FROM Warns WHERE user_id = ? ORDER BY warn_id ASC",
                (user.id,),
            )
            rows = await cursor.fetchall()
            await conn.commit()
        tc_obj = self.bot.get_guild(953632089339727953)
        warningsE = discord.Embed(title="", description="", color=0x86DEF2)
        if len(rows) == 0:
            warningsE.set_author(
                name="There are no warnings for this user.", icon_url=user.avatar
            )
        else:
            warningsE.set_author(
                name=f"{len(rows)} Warning(s) for {user.display_name} ({user.id})",
                icon_url=user.avatar,
            )
        for row in rows:
            mod = await tc_obj.fetch_member(row[0])
            user = self.bot.get_user(user.id)
            date_string = row[2]
            dt = arrow.get(date_string)
            warn_time_relative = discord.utils.format_dt(dt, "R")
            warningsE.add_field(
                name=f"Moderator: {mod}", value=f"{row[1]} - {warn_time_relative}"
            )
        await ctx.send(embed=warningsE, view=WarningView(rows, user, ctx.author.id))

    @discord.ext.commands.hybrid_command(name="mute", description="Mutes a user")
    @commands.has_any_role(
        founder_id,
        manager_id,
        admin_id,
        moderator_id,
        trial_mod_id,
        server_staff_id,
        support_id,
    )
    @app_commands.describe(user="The user that you want to mute")
    @app_commands.describe(mute_time="The amount of time you want to mute them for")
    @app_commands.describe(mute_reason="Your reason for muting them")
    async def slash_mute(
        self,
        ctx,
        user: discord.Member,
        mute_time: typing.Optional[PunishTime] = 86400,
        *,
        mute_reason: typing.Optional[str] = "No reason provided.",
    ):
        if ctx.author.top_role <= user.top_role:
            await ctx.send(
                "You can't mute someone with a role equal or higher than yours."
            )
            return
        if user == self.bot.user or user == ctx.author:
            await ctx.send("You cannot mute this user.")
            return
        if mute_time > 28 * 24 * 60 * 60:
            await ctx.send("Timeout duration cannot exceed 28 days.")
            return
        mute_until = discord.utils.utcnow() + timedelta(seconds=mute_time)
        dmEmbed = discord.Embed(
            title="You were muted in Traders Compound!", description="", color=0x86DEF2
        )
        dmEmbed.set_author(
            name="Traders Compound Moderation", icon_url=ctx.guild.icon.url
        )
        dmEmbed.add_field(
            name="You were muted for the reason:", value=f'"{mute_reason}"'
        )
        await user.send(embed=dmEmbed)
        await user.timeout(mute_until, reason=mute_reason)
        muteE = discord.Embed(
            title="", description=f"Sucessfully muted {user.mention}", color=0x86DEF2
        )
        log_embed = discord.Embed(
            title="", description="", color=0xFF0000, timestamp=datetime.now()
        )
        log_embed.set_author(name=f"Mute | {user.display_name}", icon_url=user.avatar)
        log_embed.add_field(name="User", value=f"{user.mention}")
        log_embed.add_field(name="Moderator", value=f"{ctx.author.mention}")
        log_embed.add_field(name="Reason", value=f"{mute_reason}")
        log_embed.set_footer(text=f"ID: {user.id}")
        await ctx.message.delete()
        msg = await ctx.send(embed=muteE)
        c = self.bot.get_channel(mod_logs_id)
        await c.send(embed=log_embed)
        await asyncio.sleep(5)
        await msg.delete()

    @discord.ext.commands.hybrid_command(name="unmute", description="Unmutes a user")
    @commands.has_any_role(
        founder_id,
        manager_id,
        admin_id,
        moderator_id,
        trial_mod_id,
        server_staff_id,
        support_id,
    )
    @app_commands.describe(user="The user that you want to unmute")
    @app_commands.describe(unmute_reason="Your reason for unmuting them")
    async def slash_unmute(
        self, ctx, user: discord.Member, *, unmute_reason: str = "No reason provided."
    ):
        if ctx.author.top_role <= user.top_role:
            await ctx.send(
                "You can't unmute someone with a role equal or higher than yours."
            )
            return
        if user == self.bot.user or user == ctx.author:
            await ctx.send("You cannot unmute this user.")
            return
        await user.timeout(None, reason=unmute_reason)
        unmuteE = discord.Embed(
            title="", description=f"Sucessfully unmuted {user.mention}", color=0x86DEF2
        )
        log_embed = discord.Embed(
            title="", description="", color=0xFF0000, timestamp=datetime.now()
        )
        log_embed.set_author(name=f"Unmute | {user.display_name}", icon_url=user.avatar)
        log_embed.add_field(name="User", value=f"{user.mention}")
        log_embed.add_field(name="Moderator", value=f"{ctx.author.mention}")
        log_embed.add_field(name="Reason", value=f"{unmute_reason}")
        log_embed.set_footer(text=f"ID: {user.id}")
        await ctx.message.delete()
        c = self.bot.get_channel(mod_logs_id)
        await c.send(embed=log_embed)
        msg = await ctx.send(embed=unmuteE)
        await asyncio.sleep(5)
        await msg.delete()

    @discord.ext.commands.hybrid_command(
        name="purge", description="Purges a specified amount of messages"
    )
    @commands.has_any_role(
        founder_id,
        manager_id,
        admin_id,
        moderator_id,
        trial_mod_id,
        server_staff_id,
        support_id,
    )
    @app_commands.describe(user="The user that you want to purge messages from")
    @app_commands.describe(amount="The number of messages you want to purge")
    async def slash_purge(self, ctx, user: typing.Optional[discord.User], amount: int):
        if amount <= 0 or amount > 100:
            await ctx.send("Please provide a purge amount between 1 and 100.")
            return

        def is_user(message):
            return not user or message.author == user

        try:
            deleted = await ctx.channel.purge(limit=amount + 1, check=is_user)
            await ctx.send(
                f"Successfully deleted {len(deleted)-1} message(s)", delete_after=5
            )
        except discord.Forbidden:
            await ctx.send("I don't have permissions to delete messages.")

    @discord.ext.commands.hybrid_command(name="ban", description="Bans a user")
    @commands.has_any_role(founder_id, manager_id, admin_id, moderator_id)
    @app_commands.describe(user="The user that you want to ban")
    @app_commands.describe(ban_reason="Your reason for banning them")
    async def slash_ban(
        self, ctx, user: discord.User, *, ban_reason: str = "No reason provided."
    ):
        tc_obj = self.bot.get_guild(953632089339727953)
        obj = discord.Object(user.id)
        mem = await tc_obj.fetch_member(user.id)

        if ctx.author.top_role <= mem.top_role:
            await ctx.send(
                "You can't ban someone with a role equal or higher than yours."
            )
            return
        if user == self.bot.user or user == ctx.author:
            await ctx.send("You cannot ban this user.")
            return

        dmEmbed = discord.Embed(
            title="You were banned from Traders Compound!",
            description="",
            color=0x86DEF2,
        )
        dmEmbed.set_author(
            name="Traders Compound Moderation", icon_url=ctx.guild.icon.url
        )
        dmEmbed.add_field(
            name="You were banned for the reason:", value=f'"{ban_reason}"'
        )
        try:
            await mem.send(embed=dmEmbed)
        except:
            pass
        await tc_obj.ban(obj, reason=ban_reason)
        banE = discord.Embed(
            title="", description=f"Sucessfully banned {user.mention}", color=0xFF0000
        )
        log_embed = discord.Embed(
            title="", description="", color=0xFF0000, timestamp=datetime.now()
        )
        log_embed.set_author(name=f"Ban | {user.display_name}", icon_url=user.avatar)
        log_embed.add_field(name="User", value=f"{user.mention}")
        log_embed.add_field(name="Moderator", value=f"{ctx.author.mention}")
        log_embed.add_field(name="Reason", value=f"{ban_reason}")
        log_embed.set_footer(text=f"ID: {user.id}")
        c = self.bot.get_channel(mod_logs_id)
        await c.send(embed=log_embed)
        await ctx.message.delete()
        await ctx.send(embed=banE)

    @discord.ext.commands.hybrid_command(name="unban", description="Unbans a user")
    @commands.has_any_role(founder_id, manager_id, admin_id, moderator_id)
    @app_commands.describe(user="The user that you want to unban")
    @app_commands.describe(unban_reason="Your reason for unbanning them")
    async def slash_unban(
        self, ctx, user: discord.User, *, unban_reason: str = "No reason provided."
    ):
        obj = discord.Object(user.id)
        tc_obj = self.bot.get_guild(953632089339727953)
        try:
            await tc_obj.unban(obj, reason=unban_reason)
        except discord.HTTPException:
            await ctx.send("Failed to unban this user. Are they banned?")
            return
        unbanE = discord.Embed(
            title="", description=f"Sucessfully unbanned {user.mention}", color=0x2ECC71
        )
        log_embed = discord.Embed(
            title="", description="", color=0xFF0000, timestamp=datetime.now()
        )
        log_embed.set_author(name=f"Unban | {user.display_name}", icon_url=user.avatar)
        log_embed.add_field(name="User", value=f"{user.mention}")
        log_embed.add_field(name="Moderator", value=f"{ctx.author.mention}")
        log_embed.add_field(name="Reason", value=f"{unban_reason}")
        log_embed.set_footer(text=f"ID: {user.id}")
        c = self.bot.get_channel(mod_logs_id)
        await c.send(embed=log_embed)
        await ctx.message.delete()
        await ctx.send(embed=unbanE)

    @discord.ext.commands.hybrid_command(
        name="tempban", description="Bans a user for a specified amount of time"
    )
    @commands.has_any_role(founder_id, manager_id, admin_id, moderator_id)
    @app_commands.describe(user="The user that you want to tempban")
    @app_commands.describe(ban_time="The amount of time you want to ban them for")
    @app_commands.describe(ban_reason="Your reason for tempbanning them")
    async def slash_tempban(
        self,
        ctx,
        user: discord.User,
        ban_time: typing.Optional[PunishTime] = 604800,
        *,
        ban_reason: str = "No reason provided.",
    ):
        tc_obj = self.bot.get_guild(953632089339727953)
        obj = discord.Object(user.id)
        mem = await tc_obj.fetch_member(user.id)

        if ctx.author.top_role <= mem.top_role:
            await ctx.send(
                "You can't ban someone with a role equal or higher than yours."
            )
            return
        if user == self.bot.user or user == ctx.author:
            await ctx.send("You cannot ban this user.")
            return
        if ban_time > 28 * 24 * 60 * 60:
            await ctx.send("Ban duration cannot exceed 28 days.")
            return

        unban_time = discord.utils.utcnow() + datetime.timedelta(seconds=ban_time)

        async with aiosqlite.connect(DB) as conn:
            cursor = await conn.cursor()
            await cursor.execute(
                """INSERT INTO Tempban (user_id, unban_time) VALUES (?, ?)""",
                (
                    user.id,
                    unban_time,
                ),
            )
            await conn.commit()

        if self.tempban.is_running():
            self.tempban.restart()
        else:
            self.tempban.start()

        dmEmbed = discord.Embed(
            title="You were banned from Traders Compound!",
            description="",
            color=0x86DEF2,
        )
        dmEmbed.set_author(
            name="Traders Compound Moderation", icon_url=ctx.guild.icon.url
        )
        dmEmbed.add_field(
            name="You were banned for the reason:", value=f'"{ban_reason}"'
        )
        await mem.send(embed=dmEmbed)
        await tc_obj.ban(obj, reason=ban_reason, delete_message_seconds=0)
        banE = discord.Embed(
            title="",
            description=f"Sucessfully tempbanned {user.mention}",
            color=0xFF0000,
        )
        log_embed = discord.Embed(
            title="", description="", color=0xFF0000, timestamp=datetime.now()
        )
        log_embed.set_author(
            name=f"Tempban | {user.display_name}", icon_url=user.avatar
        )
        log_embed.add_field(name="User", value=f"{user.mention}")
        log_embed.add_field(name="Moderator", value=f"{ctx.author.mention}")
        log_embed.add_field(name="Reason", value=f"{ban_reason}")
        log_embed.set_footer(text=f"ID: {user.id}")
        c = self.bot.get_channel(mod_logs_id)
        await c.send(embed=log_embed)
        await ctx.message.delete()
        await ctx.send(embed=banE)

    @discord.ext.commands.hybrid_command(name="kick", description="Kicks a user")
    @commands.has_any_role(
        founder_id, manager_id, admin_id, moderator_id, trial_mod_id, server_staff_id
    )
    @app_commands.describe(user="The user that you want to kick")
    @app_commands.describe(kick_reason="Your reason for kicking them")
    async def slash_kick(
        self, ctx, user: discord.User, *, kick_reason: str = "No reason provided."
    ):
        tc_obj = self.bot.get_guild(953632089339727953)
        obj = discord.Object(user.id)
        mem = await tc_obj.fetch_member(user.id)

        if ctx.author.top_role <= mem.top_role:
            await ctx.send(
                "You can't kick someone with a role equal or higher than yours."
            )
            return
        if user == self.bot.user or user == ctx.author:
            await ctx.send("You cannot kick this user.")
            return

        dmEmbed = discord.Embed(
            title="You were kicked from Traders Compound!",
            description="",
            color=0x86DEF2,
        )
        dmEmbed.set_author(
            name="Traders Compound Moderation", icon_url=ctx.guild.icon.url
        )
        dmEmbed.add_field(
            name="You were kicked for the reason:", value=f'"{kick_reason}"'
        )
        await mem.send(embed=dmEmbed)
        await tc_obj.kick(obj, reason=kick_reason)
        kickE = discord.Embed(
            title="", description=f"Sucessfully kicked {user.mention}", color=0xFF0000
        )
        log_embed = discord.Embed(
            title="", description="", color=0xFF0000, timestamp=datetime.now()
        )
        log_embed.set_author(name=f"Kick | {user.display_name}", icon_url=user.avatar)
        log_embed.add_field(name="User", value=f"{user.mention}")
        log_embed.add_field(name="Moderator", value=f"{ctx.author.mention}")
        log_embed.add_field(name="Reason", value=f"{kick_reason}")
        log_embed.set_footer(text=f"ID: {user.id}")
        c = self.bot.get_channel(mod_logs_id)
        await c.send(embed=log_embed)
        await ctx.message.delete()
        await ctx.send(embed=kickE)

    @tasks.loop()
    async def tempban(self):
        async with aiosqlite.connect(DB) as conn:
            cursor = await conn.cursor()
            await cursor.execute(
                "SELECT user_id, unban_time FROM Tempban ORDER BY id ASC LIMIT 1"
            )
            row = await cursor.fetchone()
            await conn.commit()

        if not row:
            self.tempban.stop()
            return

        user_id, unban_time = row
        unban_time_dt = datetime.datetime.fromisoformat(unban_time).replace(
            tzinfo=datetime.timezone.utc
        )
        await discord.utils.sleep_until(unban_time_dt)
        obj = discord.Object(user_id)
        tc_obj = self.bot.get_guild(953632089339727953)
        await tc_obj.unban(obj, reason="Tempban Expired")

    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):
        TESTING = sys.platform == "darwin"
        if TESTING:
            return
        if guild.id != 953632089339727953:
            return
        ban_unban = self.bot.get_channel(958327840137424966)
        b_embed = discord.Embed(
            title="",
            description=f"{member.mention} {member.display_name}",
            color=0xFF0000,
        )
        b_embed.set_author(name="Member Banned", icon_url=member.avatar)
        b_embed.set_thumbnail(url=member.avatar)
        b_embed.set_footer(text=f"ID: {member.id}")
        await ban_unban.send(embed=b_embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, member):
        TESTING = sys.platform == "darwin"
        if TESTING:
            return
        if guild.id != 953632089339727953:
            return
        ban_unban = self.bot.get_channel(958327840137424966)
        ub_embed = discord.Embed(
            title="",
            description=f"{member.mention} {member.display_name}",
            color=0x2ECC71,
        )
        ub_embed.set_author(name="Member Unbanned", icon_url=member.avatar)
        ub_embed.set_thumbnail(url=member.avatar)
        ub_embed.set_footer(text=f"ID: {member.id}")
        await ban_unban.send(embed=ub_embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        TESTING = sys.platform == "darwin"
        if TESTING:
            return
        if before.author.bot:
            return
        if before.guild.id != 953632089339727953:
            return
        if before.content == after.content:
            return
        if before.channel.id == admin_chat_id:
            return
        if before.channel.id == console_id:
            return
        messages = self.bot.get_channel(958327696008568892)
        me_embed = discord.Embed(
            title=f"Message Edited in {before.channel.mention}",
            description=f"[Jump to message]({after.jump_url})",
            color=0x86DEF2,
        )
        me_embed.add_field(name="Before:", value=f"{before.content}", inline=False)
        me_embed.add_field(name="After:", value=f"{after.content}", inline=False)
        me_embed.set_author(
            name=f"{before.author.display_name}", icon_url=before.author.avatar
        )
        me_embed.set_footer(
            text=f"Author ID: {before.author.id} | Message ID: {before.id}"
        )
        await messages.send(embed=me_embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        TESTING = sys.platform == "darwin"
        if TESTING:
            return
        if message.author.bot:
            return
        if message.guild.id != 953632089339727953:
            return
        if message.channel.id == admin_chat_id:
            return
        if message.channel.id == console_id:
            return
        if message.channel.id == counting_id:
            return
        messages = self.bot.get_channel(958327696008568892)
        md_embed = discord.Embed(
            title=f"",
            description=f"Message Sent by {message.author.mention} deleted in {message.channel.mention}",
            color=0xFF0000,
        )
        md_embed.add_field(name="Content:", value=f"{message.content}", inline=False)
        md_embed.set_author(
            name=f"{message.author.display_name}", icon_url=message.author.avatar
        )
        md_embed.set_footer(
            text=f"Author ID: {message.author.id} | Message ID: {message.id}"
        )
        await messages.send(embed=md_embed)
    

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Moderation(bot))
