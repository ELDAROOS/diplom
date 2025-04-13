import pygame
import sys

# Инициализация
pygame.init()
clock = pygame.time.Clock()

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
    "idle": [f'player_idle_{i}.png' for i in range(1, 10)],
    "walk": [f'player_walk_{i}.png' for i in range(1, 11)],
    "jump": [f'player_jump_{i}.png' for i in range(1, 3)],
    "attack": [f'player_attack_{i}.png' for i in range(1, 10)],
}

ENEMY_ANIMATIONS = {
    "attack": [f"attack1_{i}.png" for i in range(1, 12)],
    "fall_back": [f"fall_back_{i}.png" for i in range(1, 5)],
    "hit": [f"hit_{i}.png" for i in range(1, 3)],
    "jump": [f"jump_{i}.png" for i in range(1, 5)],
    "ready": [f"ready_{i}.png" for i in range(1, 3)],
    "run": [f"run_{i}.png" for i in range(1, 6)],
    "stand_up": [f"stand_up_{i}.png" for i in range(1, 5)],
    "walk": [f"walk_{i}.png" for i in range(1, 6)],
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

def load_enemy_animation(folder, file_list, scale=3):
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
        self.attack_rect = pygame.Rect(0, 0, 0, 0)  # Прямоугольник атаки (изначально пустой)

    def update(self, keys, enemy=None):
        if self.is_player:
            self.player_control(keys)
        else:
            self.simple_ai()

        self.apply_gravity()
        self.animate()
        
        # Если персонаж атакует, проверим, попадала ли атака по врагу
        if self.is_attacking:
            self.check_attack(enemy)

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
        # Бар шириной 200, и отступ от верхней границы экрана
        bar_width = 200
        health_ratio = self.health / self.max_health
        health_bar_x = x_offset
        health_bar_y = 20  # Местоположение ХУД-бара в верхней части экрана
        pygame.draw.rect(surface, RED, (health_bar_x, health_bar_y, bar_width, 15))
        pygame.draw.rect(surface, GREEN, (health_bar_x, health_bar_y, bar_width * health_ratio, 15))

    def check_attack(self, enemy):
        if self.facing_right:
            # Прямоугольник атаки для правой стороны
            self.attack_rect = pygame.Rect(self.rect.x + self.rect.width, self.rect.y, 50, self.rect.height)
        else:
            # Прямоугольник атаки для левой стороны
            self.attack_rect = pygame.Rect(self.rect.x - 50, self.rect.y, 50, self.rect.height)

        # Проверяем, соприкасается ли прямоугольник атаки с врагом
        if self.attack_rect.colliderect(enemy.rect):
            enemy.take_damage(10)  # Врагу наносится урон

    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0

class Enemy(Character):
    def __init__(self, x, ground_y, name, animations_dict, is_player=False):
        super().__init__(x, ground_y, name, animations_dict, is_player)
        
        self.state = "idle"  # Начальное состояние, можно заменить на "walk" или "run" в зависимости от логики
        self.anim_frame = 0

        # Уменьшаем размер врага относительно игрока
        scale_factor = 1  # Меньше чем для игрока
        self.animations = {
            key: load_enemy_animation("enemy", ENEMY_ANIMATIONS[key], scale=scale_factor) for key in ENEMY_ANIMATIONS
        }
        self.image = self.animations["walk"][0]
        self.rect = self.image.get_rect(topleft=(x, ground_y - self.image.get_height()))

    def update(self, keys, player):
        # Логика поведения врага
        self.ai_behavior(player)

        self.apply_gravity()
        self.animate()

    def ai_behavior(self, player):
        dx = player.rect.x - self.rect.x
        dy = player.rect.y - self.rect.y
        distance = (dx**2 + dy**2)**0.5  # Расстояние до игрока

        # Если враг слишком далеко, он бежит в сторону игрока
        if distance > 200:
            self.set_state("run")
            if dx > 0:
                self.rect.x += self.speed
            else:
                self.rect.x -= self.speed

        # Если враг слишком близко, он пытается атаковать
        elif distance < 50:
            self.set_state("attack")
        else:
            self.set_state("walk")
            if dx > 0:
                self.rect.x += self.speed
            else:
                self.rect.x -= self.speed
        
        # Дайте врагу возможность двигаться вверх или вниз, чтобы обойти
        if dy > 0:
            self.rect.y += self.speed  # двигается вниз
        elif dy < 0:
            self.rect.y -= self.speed  # двигается вверх

    def set_state(self, state):
        if self.state != state:
            self.state = state
            self.anim_frame = 0

    def animate(self):
        frames = self.animations[self.state]
        self.anim_frame += self.anim_speed
        if self.anim_frame >= len(frames):
            self.anim_frame = 0
        frame = frames[int(self.anim_frame)]
        self.image = frame


# Игровой цикл
def game_loop():
    player = Character(100, GROUND_LEVEL, "player", ANIMATIONS)
    enemy = Enemy(1500, GROUND_LEVEL, "enemy", ENEMY_ANIMATIONS)

    all_sprites = pygame.sprite.Group()
    all_sprites.add(player, enemy)

    while True:
        screen.fill(GRAY)

        # Проверка выхода из игры
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Получаем состояния клавиш
        keys = pygame.key.get_pressed()

        player.update(keys, enemy)
        enemy.update(keys, player)

        all_sprites.draw(screen)
        player.draw_health(screen, 20)  # Отображение здоровья игрока
        enemy.draw_health(screen, WIDTH - 220)  # Отображение здоровья врага

        pygame.display.flip()
        clock.tick(60)

game_loop()
