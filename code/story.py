import random
import pygame
import sys
import json
from collections import defaultdict
from datetime import datetime

pygame.init()
width, height = 1280, 720
screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
pygame.display.set_caption("Предистория героя")
clock = pygame.time.Clock()

try:
    pixel_font = pygame.font.Font("resources/fonts/alagard-12px-unicode.ttf", 24)
    title_font = pygame.font.Font("resources/fonts/alagard-12px-unicode.ttf", 36)
    emoji_font = pygame.font.Font("resources/fonts/NotoColorEmoji-Regular.ttf", 24)
except:
    pygame.quit()
    sys.exit("Ошибка загрузки шрифтов!")

# ==================== ЯДРО СИСТЕМЫ ====================
class StoryEngine:
    def __init__(self):
        self.story_db = self._load_databases()
        self.name_gen = NameGenerator()
        self.skill_system = SkillSystem()
        self.dialogue_gen = DialogueGenerator()
        self.world_map = WorldMap()
        self.current_story = {}
        self.hero = {}
        self.antagonist = {}
        self.game_state = {
            "location": "",
            "inventory": [],
            "skills": [],
            "choices": []
        }

    def _load_databases(self):
        return {
            "world": {
                "biomes": ["forest", "desert", "dungeon"],
                "locations": ["таверна", "храм", "башня"],
                "dangers": ["ловушки", "загадки", "монстры"]
            },
            "npc": {
                "races": ["человек", "эльф", "гном"],
                "classes": ["воин", "маг", "плут"]
            },
            "plot": {
                "goals": ["спасение", "месть", "исследование"],
                "twists": ["измена", "пророчество", "обман"]
            }
        }

    def generate_new_story(self):
        self._generate_characters()
        self._generate_world()
        self._generate_quest()
        self._save_story()
        return self._assemble_story()

    def _generate_characters(self):
        self.hero = {
            "name": self.name_gen.generate("hero"),
            "race": random.choice(self.story_db["npc"]["races"]),
            "class": random.choice(self.story_db["npc"]["classes"]),
            "skill": self.skill_system.get_skill()
        }

        self.antagonist = {
            "name": self.name_gen.generate("villain"),
            "type": random.choice(["тиран", "демон", "коррупционер"]),
            "weakness": random.choice(["гордыня", "жадность", "страх"])
        }

    def _generate_world(self):
        biome = random.choice(self.story_db["world"]["biomes"])
        self.game_state["location"] = biome
        self.game_state["map"] = self.world_map.generate(biome)
        self.game_state["danger"] = random.choice(self.story_db["world"]["dangers"])

    def _generate_quest(self):
        self.current_story = {
            "goal": random.choice(self.story_db["plot"]["goals"]),
            "twist": random.choice(self.story_db["plot"]["twists"]),
            "stages": self._generate_stages()
        }

    def _generate_stages(self):
        return [
            "Поиск союзников",
            "Подготовка к битве",
            random.choice(["Схватка с гвардейцами", "Разгадывание древних рун"]),
            "Финальная конфронтация"
        ]

    def _assemble_story(self):
        return {
            "title": f"{self.hero['name']} и {self.antagonist['type']}",
            "content": [
                f"{self.hero['name']}, {self.hero['race']}-{self.hero['class']}, "
                f"владеющий {self.hero['skill']}, начинает путь к {self.current_story['goal']}.",

                f"Место действия: {self.game_state['location'].capitalize()} "
                f"с {self.game_state['danger']}.",

                f"Поворот сюжета: {self.current_story['twist']}! "
                f"Антагонист {self.antagonist['name']} использует {self.antagonist['weakness']}.",

                f"Первый диалог: '{self.dialogue_gen.get_dialogue('start')}'",
                
                "Этапы пути: " + " → ".join(self.current_story['stages'])
            ],
            "image": ArtGallery.get_image(self.game_state["location"]),
            "music": f"music/{self.game_state['location']}_theme.ogg"
        }

    def _save_story(self):
        filename = f"saves/story_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "hero": self.hero,
                "story": self.current_story,
                "world": self.game_state
            }, f, ensure_ascii=False, indent=2)

# ==================== ВСПОМОГАТЕЛЬНЫЕ МОДУЛИ ====================
class NameGenerator:
    def generate(self, role):
        names = {
            "hero": ["Ариан", "Герейн", "Люциэн"],
            "villain": ["Моргатус", "Зирекс", "Вельгар"]
        }
        return random.choice(names[role])

class SkillSystem:
    def get_skill(self):
        skills = {
            "воин": ["мечом света", "щитом громовержца"],
            "маг": ["огненными рунами", "ледяными шипами"],
            "плут": ["теневой маскировкой", "ядовитыми клинками"]
        }
        return random.choice(skills[random.choice(list(skills.keys()))])

class DialogueGenerator:
    def get_dialogue(self, situation):
        dialogues = {
            "start": ["Кто осмелился потревожить мои владения?", "Ищешь славы или смерти?"],
            "trade": ["Что предложишь взамен?", "Этот товар стоит твоей жизни!"]
        }
        return random.choice(dialogues[situation])

class WorldMap:
    def generate(self, biome):
        tiles = {
            "forest": ["🌳", "🌲", "🌿", "☘️"],
            "desert": ["🏜️", "🌵", "🦂", "⚱️"],
            "dungeon": ["🧱", "🗝️", "💀", "🕯️"]
        }
        return [random.choice(tiles[biome]) for _ in range(9)]

class ArtGallery:
    @staticmethod
    def get_image(biome):
        try:
            return pygame.image.load(f"resources/images/{biome}_bg.png")
        except:
            return pygame.Surface((800, 600))

# ==================== ИНТЕРФЕЙС ====================

class GameUI:
    def __init__(self):
        self.buttons = []
        self.colors = {
            "background": (30, 30, 40),
            "text": (255, 255, 200),
            "button": (80, 80, 120)
        }

    def create_interface(self, story_data):
        self.buttons = []
        self._create_button("Новая игра", (1000, 650), "new")
        self._create_button("Сохранить", (1000, 600), "save")
        self._draw_story(story_data)

    def _create_button(self, text, pos, action):
        btn_rect = pygame.Rect(pos[0], pos[1], 200, 40)
        self.buttons.append({"rect": btn_rect, "text": text, "action": action})

    def _draw_story(self, story):
        screen.blit(pygame.transform.scale(story["image"], (800, 600)), (20, 50))
        
        font_size = int(height / 20)  
        max_width = width - 100 
        
        def draw_text(surface, text, x, y, font_size, max_width):
            font = pygame.font.Font("resources/fonts/alagard-12px-unicode.ttf", font_size)
            words = text.split()
            lines = []
            current_line = ""
            
            for word in words:
                if font.size(current_line + " " + word)[0] > max_width:
                    lines.append(current_line)
                    current_line = word
                else:
                    if current_line:
                        current_line += " "
                    current_line += word
            
            lines.append(current_line)
            
            for i, line in enumerate(lines):
                text_surface = font.render(line, True, self.colors["text"])
                surface.blit(text_surface, (x, y + i * (font_size + 10)))
        
        y_pos = 60
        for line in story["content"]:
            draw_text(screen, line, 840, y_pos, font_size, max_width)
            y_pos += (font_size + 10) * ((len(line.split()) + 5) // 6) 
        
        for btn in self.buttons:
            pygame.draw.rect(screen, self.colors["button"], btn["rect"])
            text = pixel_font.render(btn["text"], True, self.colors["text"])
            screen.blit(text, (btn["rect"].x + 10, btn["rect"].y + 15))


# ==================== ОСНОВНАЯ ЛОГИКА ====================
def main():
    engine = StoryEngine()
    ui = GameUI()
    current_story = engine.generate_new_story()
    
    try:
        pygame.mixer.music.load(current_story["music"])
        pygame.mixer.music.play(-1)
    except:
        pass

    running = True
    while running:
        screen.fill(ui.colors["background"])
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for btn in ui.buttons:
                    if btn["rect"].collidepoint(mouse_pos):
                        if btn["action"] == "new":
                            current_story = engine.generate_new_story()
                        elif btn["action"] == "save":
                            engine._save_story()

        ui.create_interface(current_story)
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
    pygame.quit()
    sys.exit()
