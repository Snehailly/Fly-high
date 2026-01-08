import pygame
import sys
import random
import os

pygame.init()
pygame.mixer.init()

# ---------------- SETTINGS ----------------
WIDTH, HEIGHT = 800, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fly High")

clock = pygame.time.Clock()
FPS = 60

WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
LIGHT_BLUE = (135, 206, 250)
RED = (180, 0, 0)
GREEN = (0, 200, 0)
DARK_PURPLE = (80, 0, 120)

# ---------------- FONTS ----------------
big_font = pygame.font.SysFont("comicsansms", 52, bold=True)
medium_font = pygame.font.SysFont("comicsansms", 36, bold=True)
font = pygame.font.SysFont("comicsansms", 28, bold=True)
floating_font = pygame.font.SysFont("comicsansms", 32, bold=True)

# ---------------- HELPER TO CROP BG ----------------
def crop_image(img, crop_top, crop_bottom):
    rect = pygame.Rect(0, crop_top, img.get_width(), img.get_height() - crop_bottom)
    return img.subsurface(rect).copy()

# ---------------- LOAD IMAGES ----------------
bg_img_level1 = pygame.image.load("images/BG1.1.png")
bg_img_level1 = crop_image(bg_img_level1, 0, 50)
bg_img_level1 = pygame.transform.scale(bg_img_level1, (WIDTH, HEIGHT))

bg_img_level2 = pygame.image.load("images/BG2.png")
bg_img_level2 = crop_image(bg_img_level2, 0, 50)
bg_img_level2 = pygame.transform.scale(bg_img_level2, (WIDTH, HEIGHT))

bg_img_level3 = pygame.image.load("images/BG1.png")
bg_img_level3 = crop_image(bg_img_level3, 0, 50)
bg_img_level3 = pygame.transform.scale(bg_img_level3, (WIDTH, HEIGHT))

girl_img = pygame.transform.scale(pygame.image.load("images/witch2.png"), (115, 115))
lightning_img = pygame.transform.scale(pygame.image.load("images/lightening.png"), (60, 90))
cyclone_img = pygame.transform.scale(pygame.image.load("images/cyclone.png"), (60, 60))  # smaller cyclone

pause_img = pygame.transform.scale(pygame.image.load("images/pause.png"), (40, 40))
play_img = pygame.transform.scale(pygame.image.load("images/play.png"), (40, 40))
mute_img = pygame.transform.scale(pygame.image.load("images/mute.png"), (40, 40))
unmute_img = pygame.transform.scale(pygame.image.load("images/unmute.png"), (40, 40))

# ---------------- MUSIC ----------------
pygame.mixer.music.load("sounds/bgmusic.mp3")
pygame.mixer.music.play(-1)

# ---------------- GAME VARIABLES ----------------
GROUND_Y = 450
girl_x = 100
girl_y = GROUND_Y - 120
velocity = 0
gravity = 0.6
jump = -10

lightning_speed = 8
cyclone_speed = 6
cyclone_angle = 0
cyclone_rotation_speed = 5

score = 0
level = 1
game_started = False
game_over = False
paused = False
muted = False
waiting_for_click = False
restart_taps = 0

pause_rect = pygame.Rect(WIDTH - 50, 10, 40, 40)
mute_rect = pygame.Rect(WIDTH - 100, 10, 40, 40)

# ---------------- BEST SCORE ----------------
if not os.path.exists("best_score.txt"):
    with open("best_score.txt", "w") as f:
        f.write("0")
with open("best_score.txt", "r") as f:
    best_score = int(f.read())

# ---------------- NEW HIGHEST SCORE POPUP ----------------
new_high_score_popup_timer = 0  # timer for floating popup
new_high_score_popup_duration = 120  # 2 seconds at 60 FPS

# ---------------- OBSTACLE INIT ----------------
lightning_x = WIDTH
lightning_y = random.randint(80, GROUND_Y - 150)

cyclone_x = WIDTH + 250
cyclone_y = random.randint(80, GROUND_Y - 150)

lightning2_x = WIDTH + 600
lightning2_y = random.randint(80, GROUND_Y - 150)
show_lightning2 = False

cyclone2_x = WIDTH + 800
cyclone2_y = random.randint(80, GROUND_Y - 150)
show_cyclone2 = False

extra_spawn_timer = 0

# ---------------- PASSED FLAGS FOR +50 ----------------
lightning_passed = False
cyclone_passed = False
lightning2_passed = False
cyclone2_passed = False

# ---------------- FLOATING POINTS LIST ----------------
floating_points = []  # each element: {'x', 'y', 'value', 'timer'}

# ---------------- MAIN LOOP ----------------
running = True
while running:
    clock.tick(FPS)

    # ---------------- BACKGROUND ----------------
    if level == 1:
        screen.blit(bg_img_level1, (0, 0))
    elif level == 2:
        screen.blit(bg_img_level2, (0, 0))
    else:
        screen.blit(bg_img_level3, (0, 0))

    # ---------------- EVENTS ----------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:

            if waiting_for_click:
                waiting_for_click = False
                level += 1
                lightning_x = WIDTH
                cyclone_x = WIDTH + 250
                lightning_passed = cyclone_passed = lightning2_passed = cyclone2_passed = False
                continue

            if game_over:
                restart_taps += 1
                if restart_taps >= 2:
                    game_over = False
                    game_started = True
                    restart_taps = 0
                    score = 0
                    level = 1
                    girl_y = GROUND_Y - 120
                    velocity = 0
                    lightning_x = WIDTH
                    cyclone_x = WIDTH + 250
                    lightning_passed = cyclone_passed = lightning2_passed = cyclone2_passed = False
                    new_high_score_popup_timer = 0
                continue

            if not game_started:
                game_started = True
                score = 0
                level = 1
            elif pause_rect.collidepoint(event.pos):
                paused = not paused
            elif mute_rect.collidepoint(event.pos):
                muted = not muted
                pygame.mixer.music.pause() if muted else pygame.mixer.music.unpause()
            else:
                if not paused:
                    velocity = jump

    # ---------------- GAME LOGIC ----------------
    if game_started and not game_over and not paused and not waiting_for_click:
        velocity += gravity
        girl_y += velocity

        if girl_y < 0:
            girl_y = 0
            velocity = 0
        if girl_y > GROUND_Y - 120:
            girl_y = GROUND_Y - 120
            velocity = 0

        # ---- LIGHTNING ----
        lightning_x -= lightning_speed
        if lightning_x < -60:
            lightning_x = WIDTH + random.randint(120, 200)
            lightning_y = random.randint(80, GROUND_Y - 150)
            lightning_passed = False

        # ---- CYCLONE ----
        if level >= 2:
            cyclone_x -= cyclone_speed
            cyclone_angle = (cyclone_angle + cyclone_rotation_speed) % 360
            if cyclone_x < -80:
                cyclone_x = WIDTH + random.randint(150, 250)
                cyclone_y = random.randint(80, GROUND_Y - 150)
                cyclone_passed = False

        # ---- EXTRA OBSTACLE SPAWN LOGIC ----
        extra_spawn_timer += 1
        if extra_spawn_timer > 180:
            extra_spawn_timer = 0
            if random.choice([True, False]):
                show_lightning2 = True
                lightning2_x = WIDTH + 300
                lightning2_y = random.randint(80, GROUND_Y - 150)
                lightning2_passed = False
            if level >= 2 and random.choice([True, False]):
                show_cyclone2 = True
                cyclone2_x = WIDTH + 400
                cyclone2_y = random.randint(80, GROUND_Y - 150)
                cyclone2_passed = False

        if show_lightning2:
            lightning2_x -= lightning_speed
            if lightning2_x < -60:
                show_lightning2 = False

        if show_cyclone2:
            cyclone2_x -= cyclone_speed
            if cyclone2_x < -80:
                show_cyclone2 = False

        # ---- PASSING OBSTACLE +50 FLOATING POINTS ----
        if not lightning_passed and lightning_x + 60 < girl_x:
            lightning_passed = True
            floating_points.append({'x': lightning_x + 30, 'y': lightning_y - 20, 'value': '+50', 'timer': 30})
            score += 50
        if level >= 2 and not cyclone_passed and cyclone_x + 60 < girl_x:
            cyclone_passed = True
            floating_points.append({'x': cyclone_x + 30, 'y': cyclone_y - 20, 'value': '+50', 'timer': 30})
            score += 50
        if show_lightning2 and not lightning2_passed and lightning2_x + 60 < girl_x:
            lightning2_passed = True
            floating_points.append({'x': lightning2_x + 30, 'y': lightning2_y - 20, 'value': '+50', 'timer': 30})
            score += 50
        if show_cyclone2 and not cyclone2_passed and cyclone2_x + 60 < girl_x:
            cyclone2_passed = True
            floating_points.append({'x': cyclone2_x + 30, 'y': cyclone2_y - 20, 'value': '+50', 'timer': 30})
            score += 50

        # ---- DYNAMIC BEST SCORE UPDATE ----
        if score > best_score:
            best_score = score
            with open("best_score.txt", "w") as f:
                f.write(str(best_score))
            new_high_score_popup_timer = new_high_score_popup_duration  # trigger popup

        # ---- LEVEL CHECK ----
        if level == 1 and score >= 200:
            waiting_for_click = True
            level_message = ("Level 2 Unlocked!", "Tap to Continue")
        elif level == 2 and score >= 500:
            waiting_for_click = True
            level_message = ("Level 3 Unlocked!", "Tap to Continue")

        # ---- COLLISION CHECK ----
        girl_rect = pygame.Rect(girl_x, girl_y, 70, 70)
        lightning_rect = pygame.Rect(lightning_x, lightning_y, 60, 90)
        cyclone_rect = pygame.Rect(cyclone_x, cyclone_y, 60, 60)

        if girl_rect.colliderect(lightning_rect) or (level >= 2 and girl_rect.colliderect(cyclone_rect)):
            game_over = True
            restart_taps = 0
        if show_lightning2:
            lightning2_rect = pygame.Rect(lightning2_x, lightning2_y, 60, 90)
            if girl_rect.colliderect(lightning2_rect):
                game_over = True
                restart_taps = 0
        if show_cyclone2:
            cyclone2_rect = pygame.Rect(cyclone2_x, cyclone2_y, 60, 60)
            if girl_rect.colliderect(cyclone2_rect):
                game_over = True
                restart_taps = 0

    # ---------------- DRAW ----------------
    screen.blit(girl_img, (girl_x, girl_y))
    screen.blit(lightning_img, (lightning_x, lightning_y))
    if show_lightning2:
        screen.blit(lightning_img, (lightning2_x, lightning2_y))
    if level >= 2:
        rotated = pygame.transform.rotate(cyclone_img, cyclone_angle)
        rect = rotated.get_rect(center=(cyclone_x + 30, cyclone_y + 30))
        screen.blit(rotated, rect.topleft)
    if show_cyclone2:
        rotated2 = pygame.transform.rotate(cyclone_img, cyclone_angle)
        rect2 = rotated2.get_rect(center=(cyclone2_x + 30, cyclone2_y + 30))
        screen.blit(rotated2, rect2.topleft)

    # ---------------- DRAW FLOATING POINTS ----------------
    for fp in floating_points[:]:
        screen.blit(floating_font.render(fp['value'], True, YELLOW), (fp['x'], fp['y']))
        fp['y'] -= 1
        fp['timer'] -= 1
        if fp['timer'] <= 0:
            floating_points.remove(fp)

    # ---------------- TEXT COLORS ----------------
    if level == 1:
        screen.blit(font.render(f"Score: {score}", True, DARK_PURPLE), (10, 10))
        screen.blit(font.render(f"Best: {best_score}", True, DARK_PURPLE), (10, 45))
        screen.blit(font.render(f"Level: {level}", True, DARK_PURPLE), (10, 80))
    else:
        screen.blit(font.render(f"Score: {score}", True, YELLOW), (10, 10))
        screen.blit(font.render(f"Best: {best_score}", True, WHITE), (10, 45))
        screen.blit(font.render(f"Level: {level}", True, LIGHT_BLUE), (10, 80))

    screen.blit(pause_img if not paused else play_img, pause_rect)
    screen.blit(mute_img if muted else unmute_img, mute_rect)

    # ---- NEW HIGHEST SCORE FLOATING POPUP ----
    if new_high_score_popup_timer > 0:
        popup_text = medium_font.render("NEW HIGHEST SCORE!", True, GREEN)
        screen.blit(popup_text, (WIDTH//2 - popup_text.get_width()//2, HEIGHT//2 - 100))
        new_high_score_popup_timer -= 1  # countdown

    if waiting_for_click:
        screen.blit(big_font.render(level_message[0], True, GREEN),
                    big_font.render(level_message[0], True, GREEN).get_rect(center=(WIDTH//2, HEIGHT//2 - 20)))
        screen.blit(medium_font.render(level_message[1], True, GREEN),
                    medium_font.render(level_message[1], True, GREEN).get_rect(center=(WIDTH//2, HEIGHT//2 + 40)))

    if game_over:
        over_color = YELLOW if level == 1 else RED
        screen.blit(big_font.render("GAME OVER", True, over_color), (WIDTH//2 - 150, HEIGHT//2 - 80))
        screen.blit(font.render(f"SCORE: {score}", True, WHITE), (WIDTH//2 - 80, HEIGHT//2 - 20))
        screen.blit(font.render("TAP TWICE TO RESTART", True, WHITE), (WIDTH//2 - 150, HEIGHT//2 + 30))

    pygame.display.update()

pygame.quit()
sys.exit()
