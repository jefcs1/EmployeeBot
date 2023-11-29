import asyncio
import logging
import random
import sys
from datetime import timedelta
from random import randint

import discord
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


class ChatReminders(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.logger = logging.getLogger(f"EmployeeBot.{self.__class__.__name__}")
        self.bot = bot
        self.last_reminder = None

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if self.last_reminder is not None:
            time_difference = discord.utils.utcnow() - self.last_reminder
            if time_difference < timedelta(minutes=25):
                return

        main_chat_id = 953668320215830618
        main_chat_object = self.bot.get_channel(953668320215830618)
        if message.channel.id != main_chat_id:
            return


        scam_statements = [
            "No one accidentally reported your account on steam. If someone DMs you claiming you're in risk of being banned, just block them.",
            "Steam will never contact you via Steam chat or Discord!",
            "No legit support will ever ask for payment during the procedure... they would get paid by the company not by you.",
            "You NEVER have to send items 'for verification',\njust don't send items without being 100 percent sure you'll get something in return.",
            "If you're trading with a \"Big Trader\" and their steam account isn't linked, it's probably an impersonator",
            "Don't click links to a site that someone wants you to \"Check Prices\" on, it's an API scam website.",
            "Be extremely careful when someone offers a high amount of overpay 'because they can sell it for profit' or does not seem to care too much about which item and price range you choose, it's too good to be true.",
            "Don't believe people that are 'evading tradelock' by 'sending an item from a site directly to you' while being in a call. He will cancel the trade on his phone and you won't receive anything.",
            "Be extremely careful when someone asks you to convert your CS skins into TF2 items, usually this is a scam.",
            "Don't believe the private message saying 'you won a giveaway' or similar. These are scammers, when you win an official giveaway you have to participate",
            "Don't click on any kind of Discord 'Free Nitro' or 'Server invite'.",
            "No one will contact you to play in a tournament, like in FaceIt or ESEA, and don't log into any 'tournament websites'.",
            "Steam giftcards can be charged back or bought with fraudulent credit cards which mostly brings problems",
            "Triple Trading will **NEVER DM you on discord**.",
            "A good habit for Steam logins on trusted websites is the following:\n1.) Go to steamcommunity.com\n2.) Make sure you are logged in there\n3.) Go to the site where you want to log in\n4.) It should only require you to press login with your account with no need to enter the details once again",
        ]

        topggview = TopGGButton()
        topggview.add_item(
            discord.ui.Button(
                label="Vote for us on Top.gg",
                style=discord.ButtonStyle.link,
                url="https://top.gg/servers/953632089339727953/vote",
            )
        )

        supportview = SupportButton()
        supportview.add_item(
            discord.ui.Button(
                label="Our Support Channel",
                style=discord.ButtonStyle.link,
                url="https://discord.com/channels/953632089339727953/958373332321960036",
            )
        )

        topgg_embed = discord.Embed(
            title="Vote for us on Top.gg",
            description="Voting helps push our server out to more people",
            color=0x86DEF2,
        )
        topgg_embed.set_footer(text="Thank you for your support!")
        scam_embed = discord.Embed(
            title="Stay Safe from Scams!",
            description=f"{random.choice(scam_statements)}",
            color=0x86DEF2,
        )
        support_embed = discord.Embed(
            title="Have a question/concern?",
            description="Go to our support channel and open a ticket\nOur staff team is there to assist you.",
            color=0x86DEF2,
        )

        skinflow_embed = discord.Embed(
            title="Are you looking to cash out or trade your skins?",
            description='If you are looking to **instantly sell your CSGO skins** or trade your inventory for a new one, visit *Skinflow.*\n\nSkinFlow offers multiple convenient payout methods (Paypal, BTC, ETH, LTC, AdvCash) and currently offers the best rates on the market.\n\nWith code "TC" you can also get a 2% bonus when cashing out your skins, and support Traders Compound! <:HeartTC:1102665571872555099>\n### [Cash Out your Skins with This Link](https://skinflow.gg/?referral=TC)',
            color=0x86DEF2,
        )
        skinflow_embed.set_author(
            name="Skinflow - Cash Out your Skins",
            icon_url="https://cdn.discordapp.com/attachments/957350795274248292/1146798700685971518/SkinFlow_logo.png",
        )

        random_number=0
        if self.last_reminder is not None:
            time_difference = discord.utils.utcnow() - self.last_reminder
            if time_difference > timedelta(hours=6):
                random_number = 2
            else:
                random_number = randint(1,5000)
        else:
            random_number = randint(1, 5000)
        if random_number == 1:
            await main_chat_object.send(embed=support_embed, view=supportview)
        elif random_number == 2:
            await main_chat_object.send(embed=scam_embed)
        elif random_number == 3:
            await main_chat_object.send(embed=scam_embed)
        elif random_number == 6:
            await main_chat_object.send(embed=topgg_embed, view=topggview)
        elif random_number == 7:
            await main_chat_object.send(embed=skinflow_embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ChatReminders(bot))
