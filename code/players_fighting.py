import pygame
import sys
import math  # Добавляем для вычисления расстояния

# Инициализация
pygame.init()
clock = pygame.time.Clock()

# Экран
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Fighting Game: 1v1")

# Цвета
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (80, 80, 80)

# Уровень земли
GROUND_LEVEL = HEIGHT - 250

# Анимации для игроков
ANIMATIONS = {
    "idle": [f'player_idle_{i}.png' for i in range(1, 10)],
    "walk": [f'player_walk_{i}.png' for i in range(1, 11)],
    "jump": [f'player_jump_{i}.png' for i in range(1, 3)],
    "attack": [f'player_attack_{i}.png' for i in range(1, 10)],
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
    def __init__(self, x, ground_y, name, animations_dict, is_player_one=True):
        super().__init__()
        self.name = name
        self.is_player_one = is_player_one
        self.speed = 5
        self.jump_speed = -15
        self.gravity = 0.8
        self.health = self.max_health = 500
        self.vel_y = 0
        self.is_jumping = False
        self.is_attacking = False
        self.facing_right = is_player_one
        self.anim_frame = 0
        self.anim_speed = 0.2
        self.current_action = "idle"

        self.animations = {
            key: load_animation("player", ANIMATIONS[key]) for key in ANIMATIONS
        }
        self.image = self.animations["idle"][0]
        self.rect = self.image.get_rect(topleft=(x, ground_y - self.image.get_height()))
        self.attack_rect = pygame.Rect(0, 0, 0, 0)  # Оставим, но не используем для урона

    def update(self, keys, opponent):
        self.player_control(keys)
        self.apply_gravity()
        self.animate()
        
        if self.is_attacking:
            self.check_attack(opponent)

    def player_control(self, keys):
        moving = False
        if self.is_player_one:
            if keys[pygame.K_a]:
                self.rect.x -= self.speed
                self.facing_right = False
                moving = True
            if keys[pygame.K_d]:
                self.rect.x += self.speed
                self.facing_right = True
                moving = True
            if keys[pygame.K_w] and not self.is_jumping:
                self.is_jumping = True
                self.vel_y = self.jump_speed
            if keys[pygame.K_e] and not self.is_attacking:
                self.is_attacking = True
                self.set_action("attack")
            elif not keys[pygame.K_e]:
                self.is_attacking = False
        else:
            if keys[pygame.K_LEFT]:
                self.rect.x -= self.speed
                self.facing_right = False
                moving = True
            if keys[pygame.K_RIGHT]:
                self.rect.x += self.speed
                self.facing_right = True
                moving = True
            if keys[pygame.K_UP] and not self.is_jumping:
                self.is_jumping = True
                self.vel_y = self.jump_speed
            if keys[pygame.K_m] and not self.is_attacking:
                self.is_attacking = True
                self.set_action("attack")
            elif not keys[pygame.K_m]:
                self.is_attacking = False

        if self.is_attacking:
            self.set_action("attack")
        elif self.is_jumping:
            self.set_action("jump")
        elif moving:
            self.set_action("walk")
        else:
            self.set_action("idle")

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

    def draw_health(self, surface, x_offset):
        bar_width = 200
        health_ratio = self.health / self.max_health
        health_bar_x = x_offset
        health_bar_y = 20
        pygame.draw.rect(surface, RED, (health_bar_x, health_bar_y, bar_width, 15))
        pygame.draw.rect(surface, GREEN, (health_bar_x, health_bar_y, bar_width * health_ratio, 15))

    def check_attack(self, opponent):
        # Вычисляем расстояние между центрами текстур
        dx = self.rect.centerx - opponent.rect.centerx
        dy = self.rect.centery - opponent.rect.centery
        distance = math.sqrt(dx**2 + dy**2)
        
        # Радиус попадания (50 пикселей)
        hit_radius = 50
        
        # Если расстояние меньше радиуса и игрок атакует, наносим урон
        if distance < hit_radius:
            opponent.take_damage(5)

    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0

# Игровой цикл
def game_loop():
    player1 = Character(100, GROUND_LEVEL, "player1", ANIMATIONS, is_player_one=True)
    player2 = Character(1000, GROUND_LEVEL, "player2", ANIMATIONS, is_player_one=False)

    all_sprites = pygame.sprite.Group()
    all_sprites.add(player1, player2)

    while True:
        screen.fill(GRAY)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()

        player1.update(keys, player2)
        player2.update(keys, player1)

        all_sprites.draw(screen)
        player1.draw_health(screen, 20)
        player2.draw_health(screen, WIDTH - 600)  # Твоя настройка HUD-бара

        pygame.display.flip()
        clock.tick(60)

game_loop()