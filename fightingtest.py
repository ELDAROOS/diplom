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
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Загрузка кадров для анимации
def load_frames(file_paths):
    frames = []
    for file_name in file_paths:
        try:
            img = pygame.image.load(file_name)
            frames.append(img)
        except pygame.error as e:
            print(f"Ошибка загрузки изображения {file_name}: {e}")
    return frames

# Классы для персонажей
class Character(pygame.sprite.Sprite):
    def __init__(self, x, y, name, idle_frames, walk_frames, jump_frames, attack_frames, health=100, is_player=True):
        super().__init__()
        self.name = name
        self.health = health
        self.max_health = health
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
        try:
            player = char1
        except NameError:
            print("Ошибка: char1 не определен!")
            return

        # Расстояние до игрока
        dx = player.rect.x - self.rect.x
        dy = player.rect.y - self.rect.y

        distance_x = abs(dx)
        distance_y = abs(dy)

        # Простой порог для атаки (когда касается)
        attack_range = 50

        # Проверка на атаку
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
                self.vel_y = self.jump_speed  # Обновление вертикальной скорости для прыжка

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

    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0

    def display_health(self, screen):
        # Отображение полосы здоровья
        health_bar_width = 200
        health_bar_height = 20
        health_percentage = self.health / self.max_health
        pygame.draw.rect(screen, RED, (self.rect.x, self.rect.y - 30, health_bar_width, health_bar_height))
        pygame.draw.rect(screen, GREEN, (self.rect.x, self.rect.y - 30, health_bar_width * health_percentage, health_bar_height))

# Загрузка анимаций
player_idle = load_frames(['images/player_idle_1.png', 'images/player_idle_2.png'])
player_walk = load_frames(['images/player_walk_1.png', 'images/player_walk_2.png', 'images/player_walk_3.png', 'images/player_walk_4.png', 'images/player_walk_5.png', 'images/player_walk_6.png', 'images/player_walk_7.png', 'images/player_walk_8.png'])
player_jump = load_frames(['images/player_jump_1.png'])
player_attack = load_frames(['images/player_attack_1.png', 'images/player_attack_2.png'])

robot_idle = load_frames(['images/player_idle_1.png', 'images/player_idle_2.png'])
robot_walk = load_frames(['images/player_walk_1.png', 'images/player_walk_2.png', 'images/player_walk_3.png', 'images/player_walk_4.png', 'images/player_walk_5.png', 'images/player_walk_6.png', 'images/player_walk_7.png', 'images/player_walk_8.png'])
robot_jump = load_frames(['images/player_jump_1.png'])
robot_attack = load_frames(['images/player_attack_1.png', 'images/player_attack_2.png'])

# Создание персонажей
char1 = Character(100, HEIGHT - 100, 'Player1', player_idle, player_walk, player_jump, player_attack, is_player=True)
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

    # Отображаем полосы здоровья
    char1.display_health(screen)
    char2.display_health(screen)

    # Отображаем все спрайты
    all_sprites.draw(screen)

    pygame.display.flip()
    clock.tick(60)
