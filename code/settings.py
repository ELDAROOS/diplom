import pygame
import sys
from PIL import Image, ImageSequence

pygame.init()

width, height = 800, 400
screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
pygame.display.set_caption("Adventure Quest")

pygame.mixer.init()
pygame.mixer.music.load("sounds/menu_background.wav")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

gif = Image.open("textures/menu_background.gif")
frames = [pygame.image.fromstring(frame.convert("RGBA").tobytes(), frame.size, "RGBA") for frame in ImageSequence.Iterator(gif)]

frame_index = 0
fps = 10
clock = pygame.time.Clock()

# Загрузка пиксельного шрифта
pygame.font.init()
pixel_font = pygame.font.Font("fonts/alagard-12px-unicode.ttf", 36)  # Укажи путь к пиксельному шрифту

# Загрузка текстуры бумаги
button_texture = pygame.image.load("textures/menu_button.png")  # Укажи путь к текстуре

dark_button_texture = pygame.Surface((200, 50), pygame.SRCALPHA)
dark_button_texture.blit(button_texture, (0, 0))
dark_button_texture.fill((50, 50, 50, 100), special_flags=pygame.BLEND_RGBA_MULT)  # Затемнение

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

buttons = get_buttons_positions()
settings_buttons = get_settings_buttons()

in_settings = False

running = True
while running:
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

        if event.type == pygame.MOUSEBUTTONDOWN:
            if in_settings:
                if settings_buttons["Назад"].collidepoint(mouse_pos):
                    in_settings = False
            else:
                if buttons["Играть"].collidepoint(mouse_pos):
                    print("Играть нажато")
                elif buttons["Настройки"].collidepoint(mouse_pos):
                    in_settings = True
                elif buttons["Выйти"].collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

    scaled_frame = pygame.transform.scale(frames[frame_index], (width, height))
    screen.blit(scaled_frame, (0, 0))
    frame_index = (frame_index + 1) % len(frames)

    if in_settings:
        for text, rect in settings_buttons.items():
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
    else:
        for text, rect in buttons.items():
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