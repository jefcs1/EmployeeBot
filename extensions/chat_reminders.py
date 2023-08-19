import logging
import random
from random import randint
import datetime
from datetime import timedelta

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

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot:
            return

        last_chat_reminder = discord.utils.utcnow()
        
        scam_statements = [
            "No one accidentally reported you on steam. If someone DMs you claiming you're in risk of being banned, just ignore them.",
            "Steam will never contact you via Steam chat or Discord!",
            "No legit support will ever ask for payment during the procedure... they would get paid by the company not by you.",
            "You NEVER have to send items 'for verification', just don't send items without being 100 percent sure you'll get something in return.",
            "Always try and find a different account for the 'Big Trader' that you're trading with, see if it's an impersonator.",
            "All information needed can be found in the game. Don't click links to 'a site that has more information to take a screenshot' or a site that someone wants you to 'price check' on.",
            "Be extremely careful when someone offers a high amount of overpay 'because they can sell it for profit' or does not seem to care too much about which item and price range you choose, it's too good to be true.",
            "Don't believe people that are 'evading tradelock' by 'sending an item from a site directly to you' while being in a call. He will cancel the trade on his phone and you won't receive anything.",
            "Be extremely careful when someone asks you to convert your CS skins into TF2 items, usually this is a scam.",
            "Don't believe the private message saying 'you won a giveaway' or similar. These are scammers, when you win an official giveaway you have to participate",
            "Don't click on any kind of Discord 'free Nitro' or 'Server invite'.",
            "No one will contact you to play in a tournament, like in FaceIt or ESEA, and don't log into any 'tournament websites'.",
            "Steam giftcards can be charged back or bought with fraudulent credit cards which mostly brings problems"
        ]

        topggview = TopGGButton()
        topggview.add_item(discord.ui.Button(label="Vote for us on Top.gg", style=discord.ButtonStyle.link, url = "https://top.gg/servers/953632089339727953"))

        supportview = SupportButton()
        supportview.add_item(discord.ui.Button(label = "Our Support Channel", style=discord.ButtonStyle.link, url = "https://discord.com/channels/953632089339727953/958373332321960036"))

        main_chat_id = 953668320215830618
        main_chat_object = self.bot.get_channel(953668320215830618)
        if message.channel.id != main_chat_id:
            return

        topgg_embed = discord.Embed(title="Vote for us on Top.gg", description="Voting helps push our server out to more people", color=0x86def2); topgg_embed.set_footer(text="Thank you for your support!")
        scam_embed = discord.Embed(title = "Stay Safe from Scams!", description=f"{random.choice(scam_statements)}", color = 0x86def2)
        support_embed = discord.Embed(title = "Have a question/concern?", description="Go to our support channel and open a ticket\nOur staff team is there to assist you.", color = 0x86def2)


        random_number = randint(1,200)
        print(random_number)
        if random_number != 5:
            return
        else:
            chat_reminders = [(topgg_embed, topggview), (scam_embed,None), (support_embed, supportview)]
            chat_reminder = random.choice(chat_reminders)
            await main_chat_object.send(embed = chat_reminder[0], view = chat_reminder[1])
            last_chat_reminder = discord.utils.utcnow()
        
        time_difference = discord.utils.utcnow() - last_chat_reminder
        print(time_difference)
        if time_difference > timedelta(hours=2):
            chat_reminders = [(topgg_embed, topggview), (scam_embed,None), (support_embed, supportview)]
            chat_reminder = random.choice(chat_reminders)
            await main_chat_object.send(embed = chat_reminder[0], view = chat_reminder[1])


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ChatReminders(bot))
