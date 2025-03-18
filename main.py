import pygame
import sys
from game.player import Player
from game.enemy import Enemy
from game.npc import NPC
from game.level import Level

pygame.init()
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()

player = Player()
level = Level(screen_width, screen_height)
level.generate()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    player.update()
    for enemy in level.enemies:
        enemy.update()
        if enemy.rect.right < 0:
            level.enemies.remove(enemy)

    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, (255, 0, 0), (player.rect.x, player.rect.y, player.rect.width, player.rect.height))
    for platform in level.platforms:
        pygame.draw.rect(screen, (128, 128, 128), pygame.Rect(platform[0], platform[1], platform[2], platform[3]))
    for enemy in level.enemies:
        pygame.draw.rect(screen, (0, 0, 255), (enemy.rect.x, enemy.rect.y, enemy.rect.width, enemy.rect.height))
    for npc in level.npcs:
        pygame.draw.rect(screen, (0, 255, 0), (npc.rect.x, npc.rect.y, npc.rect.width, npc.rect.height))

    for npc in level.npcs:
        if player.rect.colliderect(npc.rect):
            npc.interact()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
