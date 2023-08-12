import datetime
import logging

import discord
from discord import app_commands
from discord.ext import commands, tasks

condom_server_hyperlink = (
    '[Condom Man\'s Server](https://discord.gg/A3KnHFRj "The Server For the Event")'
)
google_form_hyperlink = '[This Google Form](https://docs.google.com/forms/d/e/1FAIpQLSfp49bVzYiSFzGtIegpVoep_Bztq8EelDNyCOn6b0Vg3Mmbvw/viewform?usp=sf_link "The Google Form for the Event")'
condom_yt_hyperlink = '([Channel Link](https://www.youtube.com/channel/UC_zWEiwrnI1rqb13WERha0A "Condom Man\'s Youtube Channel"))'
dima_yt_hyperlink = (
    '([Channel Link](https://www.youtube.com/@dimawallhacks "Dima\'s Youtube Channel"))'
)
mohzy_yt_hyperlink = (
    '([Channel Link](https://www.youtube.com/@mohzycs "Mohzy\'s Youtube Channel"))'
)


class Ad(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.logger = logging.getLogger(f"EmployeeBot.{self.__class__.__name__}")

    @app_commands.command(
        name="startad", description="Starts posting the ad every 4 hours."
    )
    @app_commands.default_permissions(administrator=True)
    async def slash_startad(self, interaction: discord.Interaction):
        if self.startad.is_running():
            self.startad.restart()
        else:
            self.startad.start()

        await interaction.response.send_message("Posting started!", ephemeral=True)

    @tasks.loop(hours=4)
    async def startad(self):
        main_channel_id = 953668320215830618
        main_channel = self.bot.get_channel(main_channel_id)

        adEmbed = discord.Embed(
            title="<:tc_tada:1102929530794016870> CSGO'S GOT TALENT - WIN $150 <:tc_tada:1102929530794016870>",
            description="We are thrilled to present this fantastic event and opportunity!\nCSGO's Got Talent is an event similar to America's Got Talent,\nbut for the members of the CSGO Community.",
            color=0x86DEF2,
        )
        adEmbed.add_field(
            name="<:tc_youtube:1128402653928497242> JUDGED BY CSGO YOUTUBERS <:tc_youtube:1128402653928497242>",
            value=f"You will be showcasing your skill (Including in real life talents if you have a webcam) to three amazing judges!\n\nCONDOM MAN - {condom_yt_hyperlink}\nDIMA WALLHACKS - {dima_yt_hyperlink}\nMOHZY - {mohzy_yt_hyperlink}\nㅤ",
            inline=False,
        )
        adEmbed.add_field(
            name="<:tc_clock:1126623703996838018> HELD ON THURSDAY OF THIS WEEK! <:tc_clock:1126623703996838018>",
            value=f"The Event will be held in {condom_server_hyperlink}!\nFill out {google_form_hyperlink} to be entered and have a chance to not only **win the cash prize,** but also to be **featured in a YouTube** video!\n\nGood luck and have fun! <:HeartTC:1102665571872555099>",
            inline=False,
        )

        await main_channel.send(embed=adEmbed)

    @app_commands.command(name="stopad", description="Stops the ad from posting.")
    @app_commands.default_permissions(administrator=True)
    async def slash_stopad(self, interaction: discord.Interaction):
        if self.startad.is_running():
            self.startad.stop()
            await interaction.response.send_message(
                "Ad posting stopped. It will complete it's next post and then stop.",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                "Ad posting isn't even running ya dumbass.", ephemeral=True
            )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Ad(bot))
