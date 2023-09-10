import logging
import aiohttp
import discord
from discord.ext import commands


class Inventory(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.logger = logging.getLogger(f"EmployeeBot.{self.__class__.__name__}")
        self.bot = bot
    
    @commands.command()
    async def inv(self, ctx, id: str):
        """Gets the inventory value of a Steam Account."""
        total_price = 0

        if id is None:
            await ctx.send("Please run `!inv <steamid>`")
        else:
            msg = await ctx.send("Calculating...")
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://www.steamwebapi.com/steam/api/inventory?key=9SXVA9A2A4CGY8H9&steam_id={id}&game=csgo&sort=price_max&currency=USD') as resp:
                    if resp.status == 403:
                        await msg.edit(content="Your inventory is private!")
                        return
                    elif resp.status == 200:
                        data = await resp.json()
                        for item in data:
                            pricemedian = item.get('pricemedian', 'N/A')
                            total_price+=pricemedian
                    
                    invEmbed = discord.Embed(title=f"{ctx.author.display_name}'s Inventory", description=f"{ctx.author.mention}", color=0x86def2)
                    invEmbed.add_field(name="CSGO Inventory Value", value=f"\n**{len(data)}** Items worth **${round(total_price,2)}**")
                    invEmbed.set_author(name="TC Employee Inventory Value", icon_url=self.bot.user.avatar)
                    invEmbed.set_thumbnail(url=ctx.author.avatar)
                    await msg.edit(embed=invEmbed, content=None)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Inventory(bot))
