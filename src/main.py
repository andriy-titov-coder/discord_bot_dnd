import sys
import os

# Add src to python path to resolve imports correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import discord
from discord.ext import commands
from discord import app_commands
from config import DISCORD_TOKEN
from views.common import StoryChoiceView
from core.resources import get_resource_path
import json

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

@bot.tree.command(name="stats", description="Переглянути характеристики та інвентар вашого героя")
async def stats(interaction: discord.Interaction):
    player_file = get_resource_path(f"src/database/players/{interaction.user.id}.json")
    
    if not os.path.exists(player_file):
        await interaction.response.send_message("У вас ще немає персонажа. Створіть його за допомогою `/choice_story`.", ephemeral=True)
        return
        
    try:
        with open(player_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        stats = data.get("stats", {})
        inventory = data.get("inventory", [])
        inv_text = ", ".join(inventory) if inventory else "Порожньо"
        
        # Визначаємо звернення залежно від статі
        gender = data.get("gender", "Чоловік")
        prefix = "Ваш герой" if gender == "Чоловік" else "Ваша героїня"
        
        embed = discord.Embed(
            title=f"📊 Меню героя: {data['name']}",
            color=discord.Color.blue()
        )
        embed.add_field(name="👤 Основне", value=f"**Клас:** {data['class']}\n**Рівень:** {data.get('level', 1)}\n**Стать:** {gender}", inline=False)
        embed.add_field(name="⚔️ Характеристики", value=(
            f"❤️ HP: {stats.get('health')}/{stats.get('max_health')}\n"
            f"💪 Сила: {stats.get('strength')}\n"
            f"🏹 Спритність: {stats.get('agility')}\n"
            f"🔮 Магія: {stats.get('magic')}"
        ), inline=True)
        embed.add_field(name="🎒 Інвентар", value=inv_text, inline=True)
        
        await interaction.response.send_message(f"{prefix} **{data['name']}**:", embed=embed, ephemeral=True)
        
    except Exception as e:
        await interaction.response.send_message(f"Помилка при зчитуванні даних: {e}", ephemeral=True)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
