import discord
from discord.ui import View, Select, Button
import os
import json

# Спробуємо імпортувати відносно або через sys.path
try:
    from core.resources import load_text_resource, get_resource_path
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core.resources import load_text_resource, get_resource_path

class ClassChoiceView(View):
    def __init__(self, character_data):
        super().__init__(timeout=None)
        self.character_data = character_data

    async def complete_creation(self, interaction: discord.Interaction, class_key: str):
        # Завантажуємо дані класу
        class_path = get_resource_path(f"resources/classes/{class_key}.json")
        try:
            with open(class_path, 'r', encoding='utf-8') as f:
                class_info = json.load(f)
            
            self.character_data["class"] = class_info["class_name"]
            self.character_data["stats"] = class_info
            
            summary = (
                f"🎉 **Створення персонажа завершено!**\n\n"
                f"**Ім'я:** {self.character_data['name']}\n"
                f"**Стать:** {self.character_data['gender']}\n"
                f"**Клас:** {self.character_data['class']}\n\n"
                f"**Характеристики:**\n"
                f"❤️ Здоров'я: {class_info['health']}\n"
                f"⚔️ Сила: {class_info['strength']}\n"
                f"🏹 Спритність: {class_info['agility']}\n"
                f"🔮 Магія: {class_info['magic']}\n\n"
                f"Твоя пригода починається прямо зараз!"
            )
            await interaction.response.edit_message(content=summary, view=None)
        except Exception as e:
            await interaction.response.send_message(f"Помилка при завантаженні класу: {e}", ephemeral=True)

    @discord.ui.button(label="Воїн", style=discord.ButtonStyle.danger, emoji="⚔️")
    async def warrior_button(self, interaction: discord.Interaction, button: Button):
        await self.complete_creation(interaction, "warrior")

    @discord.ui.button(label="Маг", style=discord.ButtonStyle.primary, emoji="🔮")
    async def mage_button(self, interaction: discord.Interaction, button: Button):
        await self.complete_creation(interaction, "mage")

    @discord.ui.button(label="Лучник", style=discord.ButtonStyle.success, emoji="🏹")
    async def archer_button(self, interaction: discord.Interaction, button: Button):
        await self.complete_creation(interaction, "archer")

class GenderChoiceView(View):
    def __init__(self, character_data):
        super().__init__(timeout=None)
        self.character_data = character_data

    @discord.ui.button(label="Чоловік", style=discord.ButtonStyle.secondary, emoji="👨")
    async def male_button(self, interaction: discord.Interaction, button: Button):
        self.character_data["gender"] = "Чоловік"
        view = ClassChoiceView(self.character_data)
        await interaction.response.edit_message(content=f"Обрано стать: **{self.character_data['gender']}**. Тепер обери свій клас:", view=view)

    @discord.ui.button(label="Жінка", style=discord.ButtonStyle.secondary, emoji="👩")
    async def female_button(self, interaction: discord.Interaction, button: Button):
        self.character_data["gender"] = "Жінка"
        view = ClassChoiceView(self.character_data)
        await interaction.response.edit_message(content=f"Обрано стать: **{self.character_data['gender']}**. Тепер обери свій клас:", view=view)


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
            
            # Одразу просимо ввести ім'я
            await channel.send("Ви намагаєтесь пригадати як вас звуть:")
            
            def check(m):
                return m.author == member and m.channel == channel

            try:
                # Чекаємо на повідомлення від користувача протягом 60 секунд
                message = await interaction.client.wait_for('message', check=check, timeout=60.0)
                name = message.content
                
                if len(name) < 2 or len(name) > 32:
                    await channel.send("Ім'я має бути від 2 до 32 символів. Спробуйте розпочати заново за допомогою `/choice_story`.")
                    return

                character_data = {"name": name}
                view = GenderChoiceView(character_data)
                await channel.send(
                    f"Вітаємо, **{name}**! Оберіть стать вашого героя:",
                    view=view
                )
            except Exception as e:
                # Можна додати обробку таймауту
                pass
            
        except discord.Forbidden:
            await interaction.response.send_message("У бота немає прав на створення каналів.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Сталася помилка при створенні каналу: {e}", ephemeral=True)
