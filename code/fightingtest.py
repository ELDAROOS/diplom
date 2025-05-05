import pygame
import sys
import math
import random

# Инициализация
pygame.init()
pygame.mixer.init()
clock = pygame.time.Clock()

# Экран
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Fighting Game: Player vs AI")

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
    "attack": [f'player_attack_{i}.png' for i in range(1, 5)],
    "hard_attack": [f'player_attack_{i}.png' for i in range(6, 10)],
    "super_attack": [f'player_attack_{i}.png' for i in range(1, 5)],
    "crouch": [f'player_crouch.png' for i in range(1)],
}

# Звуки
try:
    hit_sound = pygame.mixer.Sound('resources/sounds/hit.wav')
    jump_sound = pygame.mixer.Sound('resources/sounds/jump.wav')
    pygame.mixer.music.load('resources/sounds/background.mp3')
    pygame.mixer.music.play(-1)  # Зациклить фоновую музыку
except pygame.error as e:
    print(f"Ошибка загрузки звуков: {e}")

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
        self.health = self.max_health = 300
        self.energy = 0
        self.max_energy = 100
        self.vel_y = 0
        self.is_jumping = False
        self.is_attacking = False
        self.is_heavy_attacking = False
        self.is_super_attacking = False
        self.is_blocking = False
        self.attack_cooldown = 0
        self.combo_count = 0
        self.combo_timer = 0
        self.facing_right = is_player_one
        self.anim_frame = 0
        self.anim_speed = 0.2
        self.current_action = "idle"

        self.animations = {
            key: load_animation("player", ANIMATIONS[key]) for key in ANIMATIONS
        }
        self.image = self.animations["idle"][0]
        self.rect = self.image.get_rect(topleft=(x, ground_y - self.image.get_height()))

    def update(self, keys, opponent):
        if self.is_player_one:
            self.player_control(keys)
        else:
            self.ai_control(opponent)
        self.apply_gravity()
        self.animate()

        if self.is_attacking or self.is_heavy_attacking or self.is_super_attacking:
            self.check_attack(opponent)

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo_count = 0

    def player_control(self, keys):
        moving = False
        self.is_blocking = False

        # Движение с ограничением границ
        if keys[pygame.K_a] and self.rect.x > 0:
            self.rect.x -= self.speed
            self.facing_right = False
            moving = True
        if keys[pygame.K_d] and self.rect.x < WIDTH - self.rect.width:
            self.rect.x += self.speed
            self.facing_right = True
            moving = True
        # Прыжок
        if keys[pygame.K_w] and not self.is_jumping:
            try:
                jump_sound.play()
            except:
                pass
            self.is_jumping = True
            self.vel_y = self.jump_speed
        # Легкая атака
        if keys[pygame.K_e] and not self.is_attacking and self.attack_cooldown <= 0:
            self.is_attacking = True
            self.set_action("attack")
            self.attack_cooldown = 10  # 0.17 сек
        elif not keys[pygame.K_e]:
            self.is_attacking = False
        # Тяжелая атака
        if keys[pygame.K_q] and not self.is_heavy_attacking and self.attack_cooldown <= 0:
            self.is_heavy_attacking = True
            self.set_action("attack")
            self.attack_cooldown = 30  # 0.5 сек
        elif not keys[pygame.K_q]:
            self.is_heavy_attacking = False
        # Супер-атака
        if keys[pygame.K_f] and not self.is_super_attacking and self.energy >= self.max_energy and self.attack_cooldown <= 0:
            self.is_super_attacking = True
            self.set_action("attack")
            self.attack_cooldown = 40  # 0.67 сек
        elif not keys[pygame.K_f]:
            self.is_super_attacking = False
        # Блок
        self.is_blocking = keys[pygame.K_s]

        # Логика анимаций
        if self.is_attacking or self.is_heavy_attacking or self.is_super_attacking:
            self.set_action("attack")
        elif self.is_jumping:
            self.set_action("jump")
        elif moving:
            self.set_action("walk")
        else:
            self.set_action("idle")

    def ai_control(self, player):
        distance_x = self.rect.centerx - player.rect.centerx
        distance_y = self.rect.centery - player.rect.centery
        distance = math.sqrt(distance_x**2 + distance_y**2)

        moving = False
        self.is_blocking = False

        if not hasattr(self, 'ai_state'):
            self.ai_state = "CHASING"
            self.state_timer = 0
            self.state_duration = 0

        self.state_timer += 1 / 60

        if self.ai_state == "CHASING":
            if distance <= 80 and self.attack_cooldown <= 0:
                self.ai_state = "ATTACKING"
                self.state_timer = 0
            elif random.random() < 0.01:
                self.ai_state = "FLEEING"
                self.state_timer = 0
                self.state_duration = random.uniform(0.5, 1.5)
            elif random.random() < 0.005 and distance < 100 and (player.is_attacking or player.is_heavy_attacking):
                self.ai_state = "BLOCKING"
                self.state_timer = 0
                self.state_duration = random.uniform(0.3, 0.7)
            else:
                self.move_left = distance_x > 5
                self.move_right = distance_x < -5
                moving = True

        elif self.ai_state == "ATTACKING":
            if self.attack_cooldown <= 0:
                attack_type = random.randint(0, 10)
                if self.energy >= self.max_energy and attack_type >= 8:
                    self.is_super_attacking = True
                    self.attack_cooldown = 40
                elif attack_type >= 4:
                    self.is_heavy_attacking = True
                    self.attack_cooldown = 30
                else:
                    self.is_attacking = True
                    self.attack_cooldown = 10
            if self.state_timer >= 0.5: # После небольшой паузы после атаки
                self.ai_state = "CHASING"
                self.state_timer = 0

        elif self.ai_state == "FLEEING":
            self.move_left = distance_x < 0
            self.move_right = distance_x > 0
            moving = True
            if self.state_timer >= self.state_duration:
                self.ai_state = "IDLE"
                self.state_timer = 0
                self.state_duration = random.uniform(0.5, 2)

        elif self.ai_state == "BLOCKING":
            self.is_blocking = True
            if self.state_timer >= self.state_duration or distance > 150:
                self.ai_state = "CHASING"
                self.state_timer = 0

        elif self.ai_state == "IDLE":
            if self.state_timer >= self.state_duration:
                self.ai_state = "CHASING"
                self.state_timer = 0

        # Применение движений
        if getattr(self, 'move_left', False):
            self.rect.x -= self.speed
            self.facing_right = False
            moving = True
        if getattr(self, 'move_right', False):
            self.rect.x += self.speed
            self.facing_right = True
            moving = True

        # Прыжок с небольшой вероятностью
        if self.ai_state != "JUMPING" and 70 < distance < 150 and distance_y > 30 and not self.is_jumping and random.random() < 0.015:
            try:
                jump_sound.play()
            except:
                pass
            self.is_jumping = True
            self.vel_y = self.jump_speed
            self.ai_state = "JUMPING" # Добавляем состояние прыжка

        elif self.is_jumping and self.rect.bottom >= GROUND_LEVEL:
            self.ai_state = "CHASING" # Возвращаемся в состояние преследования после прыжка
            self.state_timer = 0

        # Анимация
        if self.is_attacking or self.is_heavy_attacking or self.is_super_attacking:
            self.set_action("attack")
        elif self.is_jumping:
            self.set_action("jump")
        elif self.is_blocking:
            self.set_action("idle") # Можно добавить анимацию блока
        elif moving:
            self.set_action("walk")
        else:
            self.set_action("idle")

        # Обнуление временных переменных движения (атака и блок обрабатываются отдельно)
        self.move_left = False
        self.move_right = False
        self.is_attacking = False
        self.is_heavy_attacking = False
        self.is_super_attacking = False
        # self.is_blocking остается установленным на время действия блока

       

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
        energy_ratio = self.energy / self.max_energy
        health_bar_x = x_offset
        health_bar_y = 20
        # Подпись игрока
        font = pygame.font.Font(None, 36)
        label = "Player 1" if self.is_player_one else "AI"
        text = font.render(label, True, WHITE)
        surface.blit(text, (health_bar_x, health_bar_y - 25))
        # Бар здоровья
        pygame.draw.rect(surface, RED, (health_bar_x, health_bar_y, bar_width, 15))
        pygame.draw.rect(surface, GREEN, (health_bar_x, health_bar_y, bar_width * health_ratio, 15))
        # Бар энергии (ниже здоровья)
        pygame.draw.rect(surface, WHITE, (health_bar_x, health_bar_y + 20, bar_width, 10))
        pygame.draw.rect(surface, (0, 0, 255), (health_bar_x, health_bar_y + 20, bar_width * energy_ratio, 10))

    def check_attack(self, opponent):
        dx = self.rect.centerx - opponent.rect.centerx
        dy = self.rect.centery - opponent.rect.centery
        distance = math.sqrt(dx**2 + dy**2)
        if distance < 50:
            try:
                hit_sound.play()
            except:
                pass
            # Определяем урон
            if self.is_super_attacking:
                damage = 20
                self.energy = 0
            elif self.is_heavy_attacking:
                damage = 10
            else:
                damage = 5 + self.combo_count  # Комбо: 5, 6, 7...
                self.combo_count += 1
                self.combo_timer = 30
            opponent.take_damage(damage)
            # Добавляем энергию за удар
            self.energy += 5
            if self.energy > self.max_energy:
                self.energy = self.max_energy

    def take_damage(self, damage):
        if self.is_blocking:
            damage //= 2  # Блок уменьшает урон вдвое
        self.health -= damage
        if self.health < 0:
            self.health = 0
        # Энергия за получение урона
        self.energy += 10
        if self.energy > self.max_energy:
            self.energy = self.max_energy

# Игровой цикл
def game_loop():
    player1 = Character(100, GROUND_LEVEL, "player1", ANIMATIONS, is_player_one=True)
    ai_player = Character(1000, GROUND_LEVEL, "ai_player", ANIMATIONS, is_player_one=False)

    all_sprites = pygame.sprite.Group()
    all_sprites.add(player1, ai_player)

    game_over = False
    winner_text = None

    while True:
        screen.fill(GRAY)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and game_over:
                if event.key == pygame.K_r:  # Рестарт
                    return game_loop()  # Перезапускаем игру

        keys = pygame.key.get_pressed()

        if not game_over:
            player1.update(keys, ai_player)
            ai_player.update(None, player1)  # Ключи для ИИ не нужны

            # Проверка победы
            if player1.health <= 0 or ai_player.health <= 0:
                game_over = True
                winner = "AI Wins!" if player1.health <= 0 else "Player 1 Wins!"
                font = pygame.font.Font(None, 74)
                winner_text = font.render(winner, True, WHITE)

        all_sprites.draw(screen)
        player1.draw_health(screen, 20)
        ai_player.draw_health(screen, WIDTH - 600)

        if game_over and winner_text:
            screen.blit(winner_text, (WIDTH // 2 - winner_text.get_width() // 2, HEIGHT // 2))
            font = pygame.font.Font(None, 36)
            restart_text = font.render("Press R to Restart", True, WHITE)
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 50))

        pygame.display.flip()
        clock.tick(60)

game_loop()