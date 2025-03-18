from .enemy import Enemy
from .npc import NPC
import pygame
import random


class Level:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.platforms = []
        self.enemies = []
        self.npcs = []

    def generate(self):
        for _ in range(10):
            platform_width = random.randint(100, 300)
            platform_height = 20
            platform_x = random.randint(0, self.width - platform_width)
            platform_y = random.randint(0, self.height - platform_height)
            self.platforms.append((platform_x, platform_y, platform_width, platform_height))

        for _ in range(5):
            enemy_x = random.randint(self.width, self.width + 100)
            enemy_y = random.randint(0, self.height)
            self.enemies.append(Enemy(enemy_x, enemy_y))

        for _ in range(2):
            npc_x = random.randint(0, self.width)
            npc_y = random.randint(0, self.height)
            self.npcs.append(NPC(npc_x, npc_y, "Привет, герой!"))
