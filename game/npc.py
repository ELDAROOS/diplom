import pygame

class NPC(pygame.sprite.Sprite):
    def __init__(self, x, y, dialogue):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.dialogue = dialogue

    def interact(self):
        print(self.dialogue)
