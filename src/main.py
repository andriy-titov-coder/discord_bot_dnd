import sys
import os

# Add src to python path to resolve imports correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import discord
from discord.ext import commands
from discord import app_commands
from config import DISCORD_TOKEN
from views.common import StoryChoiceView

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Syncing slash commands
        await self.tree.sync()
        print(f"Synced slash commands for {self.user}")

bot = MyBot()

@bot.tree.command(name="choice_story", description="Виберіть історію для початку гри")
async def choice_story(interaction: discord.Interaction):
    view = StoryChoiceView()
    await interaction.response.send_message("Виберіть одну з доступних історій:", view=view, ephemeral=True)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
