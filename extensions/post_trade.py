import logging

import discord
from discord import app_commands
from discord.ext import commands


def my_cooldown(interaction: discord.Interaction):
    if interaction.user.get_role(1121860931861893190):
        return app_commands.Cooldown(3, 18000)
    elif interaction.user.get_role(1121860948370673747):
        return app_commands.Cooldown(2, 10800)
    else:
        return app_commands.Cooldown(1, 21600)


class TradePost(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.logger = logging.getLogger(f"EmployeeBot.{self.__class__.__name__}")

    @app_commands.command(
        name="posttrade", description="Post a Trade Advertisement through the bot."
    )
    @app_commands.describe(have="Seperate your items with a comma")
    @app_commands.describe(want="Seperate your items with a comma")
    @app_commands.describe(tradelink="Add your working tradelink")
    @app_commands.checks.dynamic_cooldown(my_cooldown)
    async def posttrade(
        self, interaction: discord.Interaction, have: str, want: str, tradelink: str
    ):
        await interaction.response.defer(ephemeral=True)

        have_items = have.split(",")
        want_items = want.split(",")

        avatar_bytes = await interaction.user.avatar.read()

        webhook = await interaction.channel.create_webhook(
            name=interaction.user.name, avatar=avatar_bytes
        )

        trade_message = f"**{interaction.user.name}'s Trade Advertisement**\n\n"
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

        await interaction.followup.send("Your message has been posted!", ephemeral=True)

        infoEmbed = discord.Embed(
            title="What is this?",
            description="This is a feature that lets traders post their trade advertisements\n without having to wait the full 6 hour-cooldown.\nTo get access to this yourself check out #patreon.",
            color=0x313338,
        )

        await webhook.send(content=f"{line}\n{trade_message}", embed=infoEmbed)

        await webhook.delete()

    @posttrade.error
    async def on_posttrade_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                "This command is on cooldown.", ephemeral=True
            )
        else:
            print(error)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TradePost(bot))
