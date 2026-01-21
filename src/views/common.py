import discord
from discord.ui import View, Select
import os

# Спробуємо імпортувати відносно або через sys.path
try:
    from core.resources import load_text_resource, get_resource_path
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core.resources import load_text_resource, get_resource_path

class StoryChoiceView(View):
    def __init__(self):
        super().__init__(timeout=None)
        
    @discord.ui.select(
        placeholder="Оберіть історію...",
        options=[
            discord.SelectOption(label="хто я", value="who_am_i", description="Почніть історію 'хто я'"),
            discord.SelectOption(label="На луну", value="to_the_moon", description="Почніть історію 'На луну'"),
            discord.SelectOption(label="підземний світ", value="underworld", description="Почніть історію 'підземний світ'"),
        ]
    )
    async def select_story(self, interaction: discord.Interaction, select: Select):
        story_value = select.values[0]
        story_label = [opt.label for opt in select.options if opt.value == story_value][0]
        
        if story_value != "who_am_i":
            await interaction.response.send_message(f"Історія '{story_label}' поки що в розробці. Спробуйте 'хто я'.", ephemeral=True)
            return

        guild = interaction.guild
        member = interaction.user
        
        # Налаштування прав доступу для приватного каналу
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        channel_name = f"гра-{member.name}-{story_value}".lower()
        
        # Визначаємо категорію, в якій було розпочато гру
        category = interaction.channel.category if interaction.channel else None
        
        try:
            channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites, category=category)
            await interaction.response.send_message(f"Канал для гри створено: {channel.mention}", ephemeral=True)
            
            # Завантаження ресурсів для історії "хто я"
            intro_text = load_text_resource("resources/messeges/who_am_i.txt")
            img_path = get_resource_path("resources/images/who_am_i.png")
            
            files = []
            if os.path.exists(img_path):
                files.append(discord.File(img_path))
            
            await channel.send(content=f"Вітаємо, {member.mention}! Ви розпочали історію '{story_label}'.\n\n{intro_text}", files=files)
            
        except discord.Forbidden:
            await interaction.response.send_message("У бота немає прав на створення каналів.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Сталася помилка при створенні каналу: {e}", ephemeral=True)
