import pygame
import sys
from PIL import Image, ImageSequence
import subprocess

pygame.init()

width, height = 1920, 1080
screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
pygame.display.set_caption("Adventure Quest")

pygame.mixer.init()
pygame.mixer.music.load("resources/sounds/menu_background.wav")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

# Загрузка звуковых эффектов
hover_sound = pygame.mixer.Sound("resources/sounds/button_hover.wav")  # Укажи путь к звуку наведения
hover_sound.set_volume(0.3)
click_sound = pygame.mixer.Sound("resources/sounds/button_click.wav")  # Укажи путь к звуку клика
click_sound.set_volume(0.3)

gif = Image.open("resources/images/menu_background.gif")
frames = [pygame.image.fromstring(frame.convert("RGBA").tobytes(), frame.size, "RGBA") for frame in ImageSequence.Iterator(gif)]

frame_index = 0
fps = 10
clock = pygame.time.Clock()

pygame.font.init()
pixel_font = pygame.font.Font("resources/fonts/alagard-12px-unicode.ttf", 36)

button_texture = pygame.image.load("resources/images/menu_button.png")

dark_button_texture = pygame.Surface((200, 50), pygame.SRCALPHA)
dark_button_texture.blit(button_texture, (0, 0))
dark_button_texture.fill((50, 50, 50, 100), special_flags=pygame.BLEND_RGBA_MULT)

def get_buttons_positions():
    button_width = width // 4
    button_height = height // 10
    button_x = (width - button_width) // 2
    start_y = height // 3
    spacing = button_height + 20
    
    return {
        "Играть": pygame.Rect(button_x, start_y, button_width, button_height),
        "Настройки": pygame.Rect(button_x, start_y + spacing, button_width, button_height),
        "Выйти": pygame.Rect(button_x, start_y + 2 * spacing, button_width, button_height)
    }

def get_settings_buttons():
    button_width = width // 4
    button_height = height // 10
    button_x = (width - button_width) // 2
    start_y = height // 3
    
    return {"Назад": pygame.Rect(button_x, start_y + 2 * button_height, button_width, button_height)}

def get_play_buttons():
    button_width = width // 4
    button_height = height // 10
    button_x = (width - button_width) // 2
    start_y = height // 3
    spacing = button_height + 20
    
    return {
        "Сюжетная линия": pygame.Rect(button_x, start_y, button_width, button_height),
        "Бой с другом": pygame.Rect(button_x, start_y + spacing, button_width, button_height),
        "Назад": pygame.Rect(button_x, start_y + 2 * spacing, button_width, button_height)
    }

buttons = get_buttons_positions()
settings_buttons = get_settings_buttons()
play_buttons = get_play_buttons()

in_settings = False
in_play_menu = False
last_hovered_button = None  # Для отслеживания наведения

show_story_message = False
story_message_timer = 0


def start_story():
    global show_story_message, story_message_timer
    print("Кнопка 'Сюжетная линия' нажата")  # отладка
    show_story_message = True
    story_message_timer = pygame.time.get_ticks()


def start_fighting():
    pygame.quit()
    subprocess.Popen(["python", "./code/players_fighting.py"])
    sys.exit()

running = True
while running:
    # Показываем сообщение "В разработке"
    if show_story_message:
        time_passed = pygame.time.get_ticks() - story_message_timer
        if time_passed > 3000:  # 3 секунды
            show_story_message = False
        else:
            msg_font = pygame.font.Font("resources/fonts/alagard-12px-unicode.ttf", 48)
            message = msg_font.render("Режим в разработке...", True, (255, 255, 255))
            msg_rect = message.get_rect(center=(width // 2, height // 1.2))
            screen.blit(message, msg_rect)

    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.VIDEORESIZE:
            width, height = event.w, event.h
            screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
            buttons = get_buttons_positions()
            settings_buttons = get_settings_buttons()
            play_buttons = get_play_buttons()

        if event.type == pygame.MOUSEBUTTONDOWN:
            click_sound.play()  # Звук при клике
            if in_play_menu:
                if play_buttons["Сюжетная линия"].collidepoint(mouse_pos):
                    start_story()
                elif play_buttons["Бой с другом"].collidepoint(mouse_pos):
                    start_fighting()
                elif play_buttons["Назад"].collidepoint(mouse_pos):
                    in_play_menu = False
            elif in_settings:
                if settings_buttons["Назад"].collidepoint(mouse_pos):
                    in_settings = False
            else:
                if buttons["Играть"].collidepoint(mouse_pos):
                    in_play_menu = True
                elif buttons["Настройки"].collidepoint(mouse_pos):
                    in_settings = True
                elif buttons["Выйти"].collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

    scaled_frame = pygame.transform.scale(frames[frame_index], (width, height))
    screen.blit(scaled_frame, (0, 0))
    frame_index = (frame_index + 1) % len(frames)

    # Определяем текущие кнопки для отображения
    current_buttons = play_buttons if in_play_menu else settings_buttons if in_settings else buttons

    # Проверяем наведение для звукового эффекта
    hovered_button = None
    for text, rect in current_buttons.items():
        if rect.collidepoint(mouse_pos):
            hovered_button = text
            break

    if hovered_button != last_hovered_button and hovered_button is not None:
        hover_sound.play()
    last_hovered_button = hovered_button

    # Отрисовка кнопок
    for text, rect in current_buttons.items():
        scaled_button_texture = pygame.transform.scale(button_texture, (rect.width, rect.height))
        scaled_dark_texture = pygame.transform.scale(dark_button_texture, (rect.width, rect.height))
        
        if rect.collidepoint(mouse_pos):
            screen.blit(scaled_dark_texture, (rect.x, rect.y))
            text_color = (255, 255, 255)
        else:
            screen.blit(scaled_button_texture, (rect.x, rect.y))
            text_color = (0, 0, 0)
        
        label = pixel_font.render(text, True, text_color)
        screen.blit(label, (rect.x + (rect.width - label.get_width()) // 2, rect.y + rect.height // 4))

    pygame.display.update()
    clock.tick(fps)