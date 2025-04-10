import pygame
import sys

# Инициализация
pygame.init()

# Экран
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Fighting Game")

# Цвета
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (80, 80, 80)

# Уровень земли
GROUND_LEVEL = HEIGHT - 250

ANIMATIONS = {
    "idle": ['player_idle_1.png', 'player_idle_2.png'],
    "walk": [f'player_walk_{i}.png' for i in range(1, 9)],
    "jump": ['player_jump_1.png'],
    "attack": ['player_attack_1.png', 'player_attack_2.png']
}

def load_animation(folder, file_list, scale=3):
    frames = []
    for name in file_list:
        path = f'resources/images/{folder}/{name}'
        try:
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, (img.get_width() * scale, img.get_height() * scale))
            frames.append(img)
        except pygame.error as e:
            print(f'Ошибка загрузки {path}: {e}')
    return frames

class Character(pygame.sprite.Sprite):
    def __init__(self, x, ground_y, name, animations_dict, is_player=True):
        super().__init__()
        self.name = name
        self.is_player = is_player
        self.speed = 5
        self.jump_speed = -15
        self.gravity = 0.8
        self.health = self.max_health = 100
        self.vel_y = 0
        self.is_jumping = False
        self.is_attacking = False
        self.facing_right = True
        self.anim_frame = 0
        self.anim_speed = 0.2
        self.current_action = "idle"

        self.animations = {
            key: load_animation("player", ANIMATIONS[key]) for key in ANIMATIONS
        }
        self.image = self.animations["idle"][0]
        self.rect = self.image.get_rect(topleft=(x, ground_y - self.image.get_height()))

    def update(self, keys):
        if self.is_player:
            self.player_control(keys)
        else:
            self.simple_ai()

        self.apply_gravity()
        self.animate()

    def player_control(self, keys):
        moving = False
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
            self.facing_right = False
            moving = True
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
            self.facing_right = True
            moving = True

        if keys[pygame.K_SPACE] and not self.is_jumping:
            self.is_jumping = True
            self.vel_y = self.jump_speed

        if keys[pygame.K_z] and not self.is_attacking:
            self.is_attacking = True
            self.set_action("attack")
        elif not keys[pygame.K_z]:
            self.is_attacking = False

        if self.is_attacking:
            self.set_action("attack")
        elif self.is_jumping:
            self.set_action("jump")
        elif moving:
            self.set_action("walk")
        else:
            self.set_action("idle")

    def simple_ai(self):
        player = char1
        dx = player.rect.x - self.rect.x
        if abs(dx) > 50:
            self.rect.x += self.speed if dx > 0 else -self.speed
            self.facing_right = dx > 0
            self.set_action("walk")
        else:
            self.set_action("attack")

        if not self.is_jumping and player.rect.y < self.rect.y - 50:
            self.is_jumping = True
            self.vel_y = self.jump_speed

    def apply_gravity(self):
        if self.is_jumping:
            self.rect.y += self.vel_y
            self.vel_y += self.gravity
            ground = GROUND_LEVEL - self.image.get_height()
            if self.rect.y >= ground:
                self.rect.y = ground
                self.is_jumping = False
                self.vel_y = 0

    def set_action(self, action):
        if self.current_action != action:
            self.current_action = action
            self.anim_frame = 0

    def animate(self):
        frames = self.animations[self.current_action]
        self.anim_frame += self.anim_speed
        if self.anim_frame >= len(frames):
            self.anim_frame = 0
        frame = frames[int(self.anim_frame)]
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)
        self.image = frame

    def draw_health(self, surface):
        bar_width = 200
        health_ratio = self.health / self.max_health
        pygame.draw.rect(surface, RED, (self.rect.x, self.rect.y - 20, bar_width, 15))
        pygame.draw.rect(surface, GREEN, (self.rect.x, self.rect.y - 20, bar_width * health_ratio, 15))

# Создание персонажей (опираемся на GROUND_LEVEL)
char1 = Character(100, GROUND_LEVEL, "Player", ANIMATIONS, is_player=True)
char2 = Character(600, GROUND_LEVEL, "Enemy", ANIMATIONS, is_player=False)

all_sprites = pygame.sprite.Group(char1, char2)

# Игровой цикл
clock = pygame.time.Clock()
running = True
while running:
    screen.fill(WHITE)

    # Отрисовка земли
    pygame.draw.rect(screen, GRAY, (0, GROUND_LEVEL, WIDTH, HEIGHT - GROUND_LEVEL))

    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
            running = False

    all_sprites.update(keys)
    all_sprites.draw(screen)

    # Отрисовка здоровья
    char1.draw_health(screen)
    char2.draw_health(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
