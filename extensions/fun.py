import logging

import discord  # type: ignore
from discord import app_commands
from discord.ext import commands

count = 0

class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.logger = logging.getLogger(f"EmployeeBot.{self.__class__.__name__}")
        self.bot = bot


    @app_commands.command(name="bing", description="For MaDiT")
    async def slash_bing(self, interaction: discord.Interaction):
        await interaction.response.send_message("Chilling! :icecream:")

    @commands.Cog.listener()
    async def on_message(self, message):
        global count

        tc_id = 953632089339727953
        tc = self.bot.get_guild(tc_id)


        if message.channel.id != 1157707729268392007:
            return
        if message.author == self.bot.user:
            return
        
        print(count)

        nuhuh = discord.utils.get(tc.emojis, name="Nuhuh")

        if message.content.isdigit():
            number = int(message.content)

            if number == count + 1:
                count = number

                if count in [10, 100, 500, 1000, 5000, 100000]:
                    await message.pin()
            else:
                await message.delete()
                await message.author.send(f"{nuhuh}")
        else:
            await message.delete()
            await message.author.send(f"{nuhuh}")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Fun(bot))
