import datetime
import logging
import random

import discord  # type: ignore
from discord import app_commands
from discord.ext import commands, tasks

tc_trading_channels = {
    "What channel is for what?": {
        "title": "Each Channel is for a different item value range",
        "description": "<#957348847175209030> is for items between $0 and $100, and no role is needed to post there!\n<#953632090149232731> is for items between $100 and $1000, and you need the $100 role to post there!\n<#957349993847615489> is for items above $1000, and you need the $1000 role to post there!",
    },
    "How can I get the inventory value roles?": {
        "title": "You get the inventory value role with a command",
        "description": f"Type `!inv` in <#964253555202609162> to get the role\nOr, if the bot is not working, make sure your steam is linked to discord,\nthen contact someone on the Administration Team, and they can give you the role manually!",
    },
    "What format do I use?": {
        "title": "The trade ad format is pretty simple:",
        "description": "[H] Item\n[H] Item\n\n[W] Item\n\n*put your tradelink here*",
    },
}


class TradeChannelsPersistentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TradesDropdown())


class TradesDropdown(discord.ui.Select):
    def __init__(self):
        options = []
        for label, value in tc_trading_channels.items():
            options.append(discord.SelectOption(label=label, value=label))

        super().__init__(
            placeholder="Click here to learn about our trading channels",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="persistent_view:tradingchannels",
        )

    async def callback(self, interaction: discord.Interaction):
        selected_value = interaction.data["values"][0]
        selected_question = (tc_trading_channels)[selected_value]
        selected_title = selected_question["title"]
        selected_description = selected_question["description"]

        embed = discord.Embed(
            title=f"{selected_title}",
            description=f"{selected_description}",
            color=0x86DEF2,
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)


tc_rules = {
    "Absolutely no Scamming": {
        "info": "In Traders Compound, scamming is **strictly forbidden**.\n If you are caught scamming, you will be banned without exceptions. This is a scammer-free zone, and will always be!"
    },
    "No Cash Trading": {
        "info": "Cash trading puts you at risk of being scammed, therefore **we do not allow any sort of Cash Trading**. \nSame goes for trading accounts, virtual products, etc."
    },
    "No NSFW": {
        "info": "Posting **NSFW or Gore pictures** will result in an **immediate ban**. \nThis also applies to any discussion on NSFW Content."
    },
    "No Political Discussion": {
        "info": "We do **not** tolerate talking about Political Topics or any form of debates about Politics, political views etc."
    },
    "No Spamming": {
        "info": "Sending several messages after one another in just a short period of time is counted as spam, and will likely result in a mute."
    },
    "Treat others with respect": {
        "info": "Other server members are just like you and me, Discord nerds. \nNo racism, witch trolling, sexism or hate towards any race, religion or culture.\nAny toxicity will also be harshly punished."
    },
    "Follow the Discord Guidelines and Discord ToS": {
        "info": "Anything that goes against Discord's own laws will result in an immediate ban.\n1. [Terms of Services](https://discord.com/tos)\n2. [Guidelines](https://discord.com/guidelines)"
    },
}


class PersistentViewRules(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(RulesDropdown())


class RulesDropdown(discord.ui.Select):
    def __init__(self):
        options = []
        for label, value in tc_rules.items():
            options.append(discord.SelectOption(label=label, value=label))

        super().__init__(
            placeholder="Click to view our rules",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="persistent_view:rules",
        )

    async def callback(self, interaction: discord.Interaction):
        selected_rule = interaction.data["values"][0]
        selected_info = tc_rules[selected_rule]["info"]

        embed = discord.Embed(title=f"{selected_info}", description="", color=0x86DEF2)

        await interaction.response.send_message(embed=embed, ephemeral=True)


class TopGGButton(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None


class SupportButton(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None


class DonateButton(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None


class Accessibility(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.logger = logging.getLogger(f"EmployeeBot.{self.__class__.__name__}")

    @discord.ext.commands.hybrid_command(
        name="boost", description="Tells you how to boost the server!"
    )
    async def slash_boost(self, ctx):
        booster_role = discord.utils.get(ctx.guild.roles, id=957426366494675036)
        embed = discord.Embed(title="**Server Boosting**", color=0x86DEF2)
        embed.clear_fields()
        embed.add_field(
            name="What rewards do you get from boosting the server?",
            value=f"➥ Access to Supporters-only Text-Channel.\n➥ Access to Attach Files, Images and Embed Links in any channel.\n➥ You Are Displayed Separately From other members!\n➥Awesome pink {booster_role.mention} role.",
            inline=False,
        )
        embed.add_field(
            name="**How to boost the server?** :arrow_heading_down:",
            value="This website has a great explanation:\n https://www.alphr.com/boost-discord-server/",
        )
        embed.set_footer(text="This bot was made by jef :)")
        await ctx.send(embed=embed)

    @discord.ext.commands.hybrid_command(
        name="donate", description="Tells you how to donate to the server!"
    )
    async def slash_donate(self, ctx):
        ruby_role = discord.utils.get(ctx.guild.roles, id=964257308345528320)
        sapphire_role = discord.utils.get(ctx.guild.roles, id=964257414146850857)
        emerald_role = discord.utils.get(ctx.guild.roles, id=964257226506260590)
        donator_role = discord.utils.get(ctx.guild.roles, id=1056690536905441341)
        donoEmbed = discord.Embed(title="**Donation**", color=0x86DEF2)
        donoEmbed.clear_fields()
        donoEmbed.add_field(
            name="What rewards do you get from donating?",
            value="There are multiple tiers of donators:",
            inline=False,
        )
        donoEmbed.add_field(
            name="**Donate $5+**",
            value=f"{ruby_role.mention}\n➥ Access to attach files, images and embed links in any channel.\n➥ Access to special giveaways\n➥ Access to VIP chat, where you will have a top priority response from any staff member you want.\n➥ You get a permanent {donator_role.mention} role.",
        )
        donoEmbed.add_field(
            name="**Donate $25+**",
            value=f"{sapphire_role.mention}\n➥ All other perks.\n➥You will always have a sneak peek for new Channels, Events & Projects of ours.\n➥ Feature requests, Request a feature and we will look at it with a special priority.\n➥ Can pick a custom color and icon for your name in the server!",
        )
        donoEmbed.add_field(
            name="**Donate $100+**",
            value=f"{emerald_role.mention}\n➥ All other perks.\n➥ Bypass all giveaway requirements.\n➥ Get a permanent custom role of your choosing.",
        )
        donoEmbed.set_footer(text="This bot was made by jef :)")

        donoview = DonateButton()
        donoview.add_item(
            discord.ui.Button(
                label="Donation Link",
                style=discord.ButtonStyle.link,
                url="https://steamcommunity.com/tradeoffer/new/?partner=1343868031&token=vEyHATv4",
            )
        )

        await ctx.send(embed=donoEmbed, view=donoview)

    @discord.ext.commands.hybrid_command(
        name="rules", description="Displays the server's rules!"
    )
    async def slash_rules(self, ctx):
        embed = discord.Embed(
            title="**Server Rules**",
            description="Click on the dropdown items to see specific information about our rules",
            color=0x86DEF2,
        )

        await ctx.send(embed=embed, view=PersistentViewRules())

    @discord.ext.commands.hybrid_command(
        name="overpay", description="Helps you calculate the proper amount of overpay"
    )
    @app_commands.describe(item_value="The numeric value of the item you want in USD")
    @app_commands.describe(percent="Percent overpay you need to get the item")
    async def slash_overpay(self, ctx, item_value: float, percent: int):
        item_true_value = int(item_value)
        correct_percent = 1 + int(percent) / 100
        answer = item_true_value * correct_percent
        rounded_answer = round(answer, 2)
        message_response = f"The value of the items you send for a ${int(item_value)} item with {int(percent)}% overpay is ${rounded_answer} in order for you to properly overpay!"
        await ctx.send(content=message_response)

    @discord.ext.commands.hybrid_command(
        name="tradingchannels", description="Tells you how to use our trading channels"
    )
    @app_commands.describe(member="The member you would like to ping")
    async def slash_tradingchannels(self, ctx, member: discord.Member):
        embed = discord.Embed(
            title="How to Use Our Trading Channels", description="", color=0x86DEF2
        )
        await ctx.send(
            content=f"{member.mention}", embed=embed, view=TradeChannelsPersistentView()
        )

    @discord.ext.commands.hybrid_command(
        name="topgg", description="Sends the TopGG Server Vote link"
    )
    async def slash_topgg(self, ctx):
        embed = discord.Embed(
            title="Vote for us on Top.gg",
            description="Voting helps push our server out to more people",
            color=0x86DEF2,
        )
        embed.set_footer(text="Thank you for your support!")

        view = TopGGButton()
        view.add_item(
            discord.ui.Button(
                label="Vote on Top.gg",
                style=discord.ButtonStyle.link,
                url="https://top.gg/servers/953632089339727953/vote",
            )
        )

        await ctx.send(embed=embed, view=view)

    @discord.ext.commands.hybrid_command(
        name="support", description="Redirects you to our support channel!"
    )
    async def slash_support(self, ctx):
        supportview = SupportButton()
        supportview.add_item(
            discord.ui.Button(
                label="Our Support Channel",
                style=discord.ButtonStyle.link,
                url="https://discord.com/channels/953632089339727953/958373332321960036",
            )
        )
        support_embed = discord.Embed(
            title="Have a question/concern?",
            description="Go to our support channel and open a ticket\nOur staff team is there to assist you.",
            color=0x86DEF2,
        )

        await ctx.send(embed=support_embed, view=supportview)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Accessibility(bot))
