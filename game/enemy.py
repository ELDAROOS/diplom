import pygame
import random

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill((0, 0, 255))
        self.image.set_colorkey((0, 0, 255))
        # Загрузка текстуры врага
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = random.randint(1, 3)

    def update(self):
        self.rect.x -= self.speed
