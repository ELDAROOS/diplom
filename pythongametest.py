import pygame
import random

# Инициализация Pygame
pygame.init()

# Параметры экрана
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Процедурная генерация платформера с двойным прыжком")

# Цвета
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)  # Цвет для индикатора

# Игровые параметры
player_width = 50
player_height = 50
player_x = 100
player_y = screen_height - player_height - 100
player_velocity = 5
player_jump_velocity = 10
gravity = 1
player_velocity_y = 0
on_ground = False
jump_height = 150  # Максимальная высота прыжка
level_length = 5000  # Длина уровня (в пикселях)
max_platform_height = 400  # Ограничение по максимальной высоте платформы

# Платформы
platform_width_range = (80, 200)  # Диапазон ширины платформ
platform_height = 20
platforms = []
ladders = []  # Лестницы

# Переменная для отслеживания прыжков
jump_count = 0

# Генерация платформ с учетом того, чтобы они были проходимыми
def generate_platforms():
    platforms.clear()
    ladders.clear()
    y = screen_height - 50  # Начальная высота для первой платформы
    prev_platform_x = 0  # Для отслеживания, где была последняя платформа

    # Создаем землю под персонажем
    platforms.append(pygame.Rect(0, screen_height - platform_height, screen_width * 2, platform_height))

    # Генерация платформ
    for i in range(30):  # Увеличили количество платформ
        gap = random.randint(150, 250)  # Генерация случайного расстояния между платформами
        prev_platform_x += gap
        platform_height_offset = random.randint(-50, 100)  # Рандомизация высоты платформы
        platform_height_offset = max(0, platform_height_offset)  # Платформа не будет под землей
        
        # Ограничение по высоте платформ
        if platform_height_offset > max_platform_height:
            platform_height_offset = max_platform_height

        platform_width = random.randint(*platform_width_range)  # Рандомная ширина платформы
        platforms.append(pygame.Rect(prev_platform_x, y - platform_height_offset, platform_width, platform_height))
        y -= random.randint(100, jump_height)  # Высота между платформами

        # Генерация лестницы (вертикальная платформа для подъема)
        if random.random() < 0.2:  # Лестницы будут появляться с вероятностью 20%
            ladder_height = random.randint(60, 150)  # Высота лестницы
            ladders.append(pygame.Rect(prev_platform_x + platform_width // 2 - 10, y - ladder_height, 20, ladder_height))

# Игровой цикл
def game_loop():
    global player_x, player_y, player_velocity_y, on_ground, jump_count

    generate_platforms()

    clock = pygame.time.Clock()
    running = True
    camera_x = 0  # Начальная позиция камеры
    start_ticks = pygame.time.get_ticks()  # Засекаем время начала игры
    ladder_climb_speed = 3  # Скорость подъема по лестнице

    # Длительность уровня (больше времени на прохождение)
    game_time_limit = 10 * 60  # Увеличено время до 10 минут (600 секунд)
    level_progress = 0  # Прогресс по уровню
    level_speed = 2  # Скорость, с которой будет двигаться уровень

    while running:
        screen.fill(WHITE)
        
        # Проверка на истечение времени
        seconds = (pygame.time.get_ticks() - start_ticks) // 1000
        if seconds >= game_time_limit:
            running = False  # Игра заканчивается после 10 минут

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Управление игроком
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_x -= player_velocity
        if keys[pygame.K_RIGHT]:
            player_x += player_velocity
        
        # Гравитация
        player_velocity_y += gravity
        player_y += player_velocity_y
        
        # Проверка на платформы (если персонаж касается платформы)
        on_ground = False
        for plat in platforms:
            if plat.colliderect(pygame.Rect(player_x, player_y, player_width, player_height)) and player_velocity_y >= 0:
                on_ground = True
                player_velocity_y = 0
                player_y = plat.top - player_height
                jump_count = 0  # Сбрасываем счетчик прыжков при касании земли
                break

        # Проверка на лестницу
        if not on_ground:
            for ladder in ladders:
                if ladder.colliderect(pygame.Rect(player_x, player_y, player_width, player_height)):
                    on_ground = True
                    if keys[pygame.K_UP]:
                        player_y -= ladder_climb_speed
                    break

        # Прыжок
        if on_ground and keys[pygame.K_SPACE]:
            player_velocity_y = -player_jump_velocity
            jump_count = 1  # Первый прыжок
        elif not on_ground and jump_count == 0 and keys[pygame.K_SPACE]:
            player_velocity_y = -player_jump_velocity  # Второй прыжок в воздухе
            jump_count = 1  # Устанавливаем второй прыжок
        elif not on_ground and jump_count == 1 and keys[pygame.K_SPACE]:
            player_velocity_y = -player_jump_velocity  # Второй прыжок
            jump_count = 2  # Теперь нельзя прыгать снова до касания с землей
#diplom
        # Отображение игрока
        pygame.draw.rect(screen, BLUE, (player_x - camera_x, player_y, player_width, player_height))

        # Отображение платформ
        for plat in platforms:
            pygame.draw.rect(screen, BROWN, (plat.x - camera_x, plat.y, plat.width, platform_height))

        # Отображение лестниц
        for ladder in ladders:
            pygame.draw.rect(screen, (139, 0, 0), (ladder.x - camera_x, ladder.y, ladder.width, ladder.height))

        # Камера следует за игроком
        if player_x - camera_x > screen_width - 200:  # Камера будет следовать, если игрок слишком близко к правому краю
            camera_x += player_velocity
        if player_x - camera_x < 200:  # Камера будет следовать, если игрок слишком близко к левому краю
            camera_x -= player_velocity

        # Генерация новых платформ, если игрок двигается далеко влево или вправо
        if player_x > platforms[-1].x - screen_width:
            generate_platforms()

        # Отображение финиша
        finish_line_x = level_length - 200
        pygame.draw.rect(screen, RED, (finish_line_x - camera_x, 0, 10, screen_height))
        
        # Проверка на финиш
        if player_x >= finish_line_x:
            font = pygame.font.SysFont(None, 55)
            text = font.render("Поздравляем, вы прошли уровень!", True, (0, 255, 0))
            screen.blit(text, (screen_width // 2 - text.get_width() // 2, screen_height // 2))

        # Индикатор двойного прыжка
        if not on_ground and jump_count == 1:
            pygame.draw.circle(screen, YELLOW, (screen_width - 30, screen_height - 30), 10)  # Индикатор на экране
            font = pygame.font.SysFont(None, 30)
            text = font.render("Двойной прыжок", True, YELLOW)
            screen.blit(text, (screen_width - text.get_width() - 15, screen_height - 60))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

# Запуск игры
game_loop()
