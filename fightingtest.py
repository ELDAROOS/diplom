import pygame
import sys
import random

# Инициализация Pygame
pygame.init()

# Размеры экрана
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Fighting Game')

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Загрузка кадров для анимации
def load_frames(file_paths):
    return [pygame.image.load(path) for path in file_paths]

# Классы для персонажей
class Character(pygame.sprite.Sprite):
    def __init__(self, x, y, name, idle_frames, walk_frames, jump_frames, attack_frames, is_player=True):
        super().__init__()
        self.name = name
        self.is_jumping = False
        self.is_attacking = False
        self.is_player = is_player
        self.speed = 5  # Скорость движения
        self.animation_frame = 0
        self.animation_speed = 0.2
        self.gravity = 0.8
        self.jump_speed = -15
        self.vel_y = 0
        self.facing_right = True
        self.ai_cooldown = 0  # Таймер для паузы между действиями ИИ

        self.scale_factor = 3
        
        # Масштабируем все кадры
        self.idle_frames = [pygame.transform.scale(img, (img.get_width() * self.scale_factor, img.get_height() * self.scale_factor)) for img in idle_frames]
        self.walk_frames = [pygame.transform.scale(img, (img.get_width() * self.scale_factor, img.get_height() * self.scale_factor)) for img in walk_frames]
        self.jump_frames = [pygame.transform.scale(img, (img.get_width() * self.scale_factor, img.get_height() * self.scale_factor)) for img in jump_frames]
        self.attack_frames = [pygame.transform.scale(img, (img.get_width() * self.scale_factor, img.get_height() * self.scale_factor)) for img in attack_frames]

        self.facing_right = True  # Флаг для отслеживания направления взгляда

        self.frames = {
            "idle": self.idle_frames,
            "walk": self.walk_frames,
            "jump": self.jump_frames,
            "attack": self.attack_frames,
            "current": self.idle_frames  # по умолчанию
        }
        self.image = self.frames["idle"][0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y - self.rect.height + 50

    def update(self, keys):
        if self.is_player:
            self.player_controls(keys)
        else:
            self.robot_ai()

        self.animate()

    def player_controls(self, keys):
        # Управление для игрока
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
            self.set_animation("walk")
            if self.facing_right:
                self.flip_character()  # Переворачиваем персонажа
        elif keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
            self.set_animation("walk")
            if not self.facing_right:
                self.flip_character()  # Переворачиваем персонажа
        else:
            self.set_animation("idle")

        if keys[pygame.K_SPACE] and not self.is_jumping:
            self.is_jumping = True
            self.vel_y = self.jump_speed  # Прыжок

        if self.is_jumping:
            self.rect.y += self.vel_y  # Применение вертикальной скорости
            self.vel_y += self.gravity  # Применение гравитации

            ground_y = HEIGHT - self.rect.height + -50  # Уровень земли с учётом размера спрайта
            if self.rect.y >= ground_y:
                self.rect.y = ground_y
                self.is_jumping = False
                self.vel_y = 0

        if keys[pygame.K_z] and not self.is_attacking:  # Атака
            self.is_attacking = True
            self.set_animation("attack")
        elif not keys[pygame.K_z]:
            self.is_attacking = False
            if self.is_jumping:
                self.set_animation("jump")
            else:
                self.set_animation("idle")

    def robot_ai(self):
        # Получаем игрока (предположим, что он всегда char1)
        player = char1

        # Расстояние до игрока
        dx = player.rect.x - self.rect.x
        dy = player.rect.y - self.rect.y

        distance_x = abs(dx)
        distance_y = abs(dy)

        # Простой порог для атаки (когда касается)
        attack_range = 50

        if distance_x < attack_range and distance_y < 100:
            self.set_animation("attack")
            self.is_attacking = True
        else:
            self.is_attacking = False
            # Преследуем игрока
            if dx > 0:
                self.rect.x += self.speed
                if not self.facing_right:
                    self.flip_character()
            else:
                self.rect.x -= self.speed
                if self.facing_right:
                    self.flip_character()
            self.set_animation("walk")

            # Простая логика прыжка, если игрок выше
            if dy < -50 and not self.is_jumping:
                self.is_jumping = True
                self.vel_y = self.jump_speed


    def flip_character(self):
        # Переворачиваем персонажа
        self.facing_right = not self.facing_right
        for i in range(len(self.frames)):
            self.frames[list(self.frames.keys())[i]] = [pygame.transform.flip(frame, True, False) for frame in self.frames[list(self.frames.keys())[i]]]

    def set_animation(self, action):
        if self.is_attacking:
            action = "attack"
        elif self.is_jumping:
            action = "jump"
        elif self.rect.x == WIDTH // 2:
            action = "walk"

        if self.frames[action] != self.frames.get("current", []):
            self.animation_frame = 0
            self.frames["current"] = self.frames[action]

    def animate(self):
        # Плавная анимация
        self.animation_frame += self.animation_speed
        if self.animation_frame >= len(self.frames["current"]):
            self.animation_frame = 0
        self.image = self.frames["current"][int(self.animation_frame)]

# Создание персонажей
player_idle = load_frames(['1.png', '2.png'])
player_walk = load_frames(['3.png', '4.png', '5.png', '9.png', '10.png', '11.png', '12.png', '13.png'])
player_jump = load_frames(['6.png'])
player_attack = load_frames(['7.png', '8.png'])
char1 = Character(100, HEIGHT - 100, 'Player1', player_idle, player_walk, player_jump, player_attack, is_player=True)

robot_idle = load_frames(['1.png', '2.png'])
robot_walk = load_frames(['3.png', '4.png', '5.png', '9.png', '10.png', '11.png', '12.png', '13.png'])
robot_jump = load_frames(['6.png'])
robot_attack = load_frames(['7.png', '8.png'])
char2 = Character(600, HEIGHT - 100, 'Robot', robot_idle, robot_walk, robot_jump, robot_attack, is_player=False)

# Группа персонажей
all_sprites = pygame.sprite.Group()
all_sprites.add(char1, char2)

# Основной игровой цикл
clock = pygame.time.Clock()
while True:
    screen.fill(WHITE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    char1.update(keys)  # Управление игроком
    char2.update(keys)  # Поведение робота

    all_sprites.draw(screen)
    
    pygame.display.flip()
    clock.tick(60)
