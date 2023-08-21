import datetime
import logging

import discord  # type: ignore
from discord import app_commands
from discord.ext import commands


class TopGGButton(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

class SupportButton(discord.ui.View):
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
    async def slash_boost(self,ctx):
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
        sapphire_role = discord.utils.get(
            ctx.guild.roles, id=964257414146850857
        )
        emerald_role = discord.utils.get(ctx.guild.roles, id=964257226506260590)
        donator_role = discord.utils.get(
            ctx.guild.roles, id=1056690536905441341
        )
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
        donoEmbed.add_field(
            name="**Donation Link** :arrow_heading_down:",
            value="[Send a Trade Offer here](https://steamcommunity.com/tradeoffer/new/?partner=1212841160&token=Ap7pvLax)",
        )
        donoEmbed.set_footer(text="This bot was made by jef :)")
        await ctx.send(embed=donoEmbed)

    @discord.ext.commands.hybrid_command(name="rules", description="Displays the server's rules!")
    async def slash_rules(self, ctx):
        embed = discord.Embed(
            title="**Server Rules**",
            description="Here are the server's rules.",
            color=0x86DEF2,
        )
        embed.clear_fields()
        embed.set_thumbnail(url=ctx.guild.icon)
        embed.add_field(
            name="**1) Absolutely no Scamming**",
            value="In Traders Compound, scamming is **strictly forbidden**. If you are caught scamming, you will be banned without exceptions. This is a scammer-free zone, and will always be!",
            inline=False,
        )
        embed.add_field(
            name="**2) No Cash Trading**",
            value="Cash trading puts you at risk of being scammed, therefore **we do not allow any sort of Cash Trading**. Same goes for trading accounts, virtual products, etc.",
            inline=False,
        )
        embed.add_field(
            name="**3) No NSFW**",
            value="Posting **NSFW or Gore pictures** will result in an **immediate ban**. This also applies to any discussion on NSFW Content.",
            inline=False,
        )
        embed.add_field(
            name="**4) No Political Discussion**",
            value="We do **not** tolerate talking about Political Topics or any form of debates about Politics, political views etc.",
            inline=False,
        )
        embed.add_field(
            name="**5) No Spamming**",
            value="Sending several messages after one another in just a short period of time is counted as spam, and will likely result in a mute.",
            inline=False,
        )
        embed.add_field(
            name="**6) Treat others with respect**",
            value="Other server members are just like you and me, Discord nerds. No racism, witch trolling, sexism or hate towards any race, religion or culture.\nAny toxicity will also be harsly punished.",
            inline=False,
        )
        embed.add_field(
            name="• **Follow the Discord Guidelines and Discord ToS**",
            value="Anything that goes against Discord's own laws will result in an immediate ban.\n1. [Terms of Services](https://discord.com/tos)\n2. [Guidelines](https://discord.com/guidelines)",
            inline=False,
        )
        embed.set_footer(text="This bot was made by jef :)")
        await ctx.send(embed=embed, ephemeral=True)

    @discord.ext.commands.hybrid_command(
        name="overpay", description="Helps you calculate the proper amount of overpay"
    )
    @app_commands.describe(item_value="The numeric value of the item you want in USD")
    @app_commands.describe(percent="Percent overpay you need to get the item")
    async def slash_overpay(
        self, ctx, item_value: float, percent: int
    ):
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
    async def slash_tradingchannels(
        self, ctx, member: discord.Member
    ):
        tradeEmbed = discord.Embed(
            title=f"**This is how our trading channels work!**", color=0x86DEF2
        )
        role = ctx.guild.get_role(984591820744966184)
        tradeEmbed.clear_fields()
        tradeEmbed.add_field(
            name="**What channel is for what?**",
            value="<#957348847175209030> is for items between $0 and $100, and no role is needed to post there!\n<#953632090149232731> is for items between $100 and $1000, and you need the $100 role to post there!\n<#957349993847615489> is for items above $1000, and you need the $1000 role to post there!",
            inline=False,
        )
        tradeEmbed.add_field(
            name="**How can I get the inventory value roles?**",
            value=f"Type `-inv` in <#964253555202609162> to get the role\nOr, if the bot is not working, make sure your steam is linked to discord,\nthen contact someone on the {role.mention}, and they can give you the role manually!",
            inline=False,
        )
        tradeEmbed.add_field(
            name="**MAKE SURE YOU FOLLOW THE CORRECT FORMAT**",
            value="**You can find the correct format in the pinned message of the respective channel.**",
        )
        tradeEmbed.add_field(
            name="**DONT SPAM THE SAME AD**",
            value="**If you use the same ad for multiple channels, it will get deleted.\nEach channel should be displaying a different price range of items.**",
        )
        tradeEmbed.set_footer(text="This bot was made by jef :)")
        await ctx.send(
            content=f"{member.mention}", embed=tradeEmbed
        )


    @discord.ext.commands.hybrid_command(name = "topgg", description="Sends the TopGG Server Vote link")
    async def slash_topgg(self, ctx):

        embed = discord.Embed(title = "Vote for us on Top.gg", description = "Voting helps push our server out to more people", color = 0x86def2)
        embed.set_footer(text="Thank you for your support!")

        view = TopGGButton()
        view.add_item(discord.ui.Button(label="Vote on Top.gg", style=discord.ButtonStyle.link, url = "https://top.gg/servers/953632089339727953"))

        await ctx.send(embed=embed,view=view)

    @discord.ext.commands.hybrid_command(name = "support", description = "Redirects you to our support channel!")
    async def slash_support(self, ctx):

        supportview = SupportButton()
        supportview.add_item(discord.ui.Button(label = "Our Support Channel", style=discord.ButtonStyle.link, url = "https://discord.com/channels/953632089339727953/958373332321960036"))
        support_embed = discord.Embed(title = "Have a question/concern?", description="Go to our support channel and open a ticket\nOur staff team is there to assist you.", color = 0x86def2)

        await ctx.send(embed=support_embed, view=supportview)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Accessibility(bot))
