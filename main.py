import pygame
import sys
import random
import os

pygame.init()
pygame.mixer.init()

# ---------------- SETTINGS ----------------
WIDTH, HEIGHT = 1000, 650
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
BLACK = (0, 0, 0)

# ---------------- FONTS ----------------
big_font = pygame.font.SysFont("comicsansms", 40, bold=True)
medium_font = pygame.font.SysFont("comicsansms", 36, bold=True)
font = pygame.font.SysFont("comicsansms", 28, bold=True)
floating_font = pygame.font.SysFont("comicsansms", 32, bold=True)

# ---------------- HELPER ----------------
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
cyclone_img = pygame.transform.scale(pygame.image.load("images/cyclone.png"), (60, 60))
earthquake_img = pygame.transform.scale(pygame.image.load("images/earthquake.png"), (90, 70))
heart_img = pygame.transform.scale(pygame.image.load("images/heart.png"), (35, 35))
pause_img = pygame.transform.scale(pygame.image.load("images/pause.png"), (40, 40))
play_img = pygame.transform.scale(pygame.image.load("images/play.png"), (40, 40))
mute_img = pygame.transform.scale(pygame.image.load("images/mute.png"), (40, 40))
unmute_img = pygame.transform.scale(pygame.image.load("images/unmute.png"), (40, 40))
quiz_icon_img = pygame.transform.scale(pygame.image.load("images/quiz.png"), (50, 50))

# ---------------- MUSIC ----------------
pygame.mixer.music.load("sounds/bgmusic.mp3")
pygame.mixer.music.play(-1)

# ---------------- GAME VARIABLES ----------------
GROUND_Y = 600
girl_x = WIDTH // 2
girl_y = GROUND_Y - 120

lightning_speed = 7
cyclone_speed = 6
earthquake_speed = 8
level3_boost = 2

score = 0
level = 1
lives = 3

game_started = False
game_over = False
paused = False
muted = False
waiting_for_click = False
restart_taps = 0
dragging = False

quiz_mode = False
quiz_index = 0

pause_rect = pygame.Rect(WIDTH - 50, 10, 40, 40)
mute_rect = pygame.Rect(WIDTH - 100, 10, 40, 40)
quiz_icon_rect = pygame.Rect(20, 120, 80, 50)  # always visible top-left

# ---------------- BEST SCORE ----------------
if not os.path.exists("best_score.txt"):
    with open("best_score.txt", "w") as f:
        f.write("0")

with open("best_score.txt", "r") as f:
    best_score = int(f.read())

# ---------------- POPUP ----------------
new_high_score_popup_timer = 0
new_high_score_popup_duration = 120

# ---------------- OBSTACLES ----------------
lightning_x = random.randint(50, WIDTH - 100)
lightning_y = -100
cyclone_x = random.randint(50, WIDTH - 100)
cyclone_y = -200
earthquake_x = random.randint(50, WIDTH - 120)
earthquake_y = -300
lightning_passed = False
cyclone_passed = False
earthquake_passed = False
floating_points = []

blink_timer = 0
show_text = True

# ---------------- QUIZ QUESTIONS ----------------
all_quiz_questions = [
     {"q": "What should you wear when it rains?", "options": ["Raincoat", "Sunglasses", "Boots"], "answer": 0},
    {"q": "What keeps us cool in summer?", "options": ["Fan", "Boots", "Raincoat"], "answer": 0},
    {"q": "What falls from clouds?", "options": ["Water", "Sand", "Fire"], "answer": 0},
    {"q": "Which is hot in the sky?", "options": ["Sun", "Moon", "Cloud"], "answer": 0},
    {"q": "What do we see after rain sometimes?", "options": ["Rainbow", "Snow", "Thunder"], "answer": 0},
    {"q": "What is white and falls from the sky in winter?", "options": ["Snow", "Rain", "Fire"], "answer": 0},
    {"q": "What moves the trees on a windy day?", "options": ["Wind", "Sun", "Clouds"], "answer": 0},
    {"q": "What do you use when it is sunny outside?", "options": ["Sunglasses", "Umbrella", "Raincoat"], "answer": 0},
    {"q": "Which is safe to touch?", "options": ["Sand", "Lightning", "Fire"], "answer": 0},
    {"q": "What makes a loud noise in storm?", "options": ["Thunder", "Cloud", "Rain"], "answer": 0},
    {"q": "What can hurt you if it is very hot?", "options": ["Fire", "Water", "Cloud"], "answer": 0},
    {"q": "What do you wear on your feet when it rains?", "options": ["Boots", "Shoes", "Gloves"], "answer": 0},
    {"q": "What helps you dry when wet?", "options": ["Towel", "Umbrella", "Fan"], "answer": 0},
    {"q": "What floats in the sky?", "options": ["Cloud", "Sun", "Tree"], "answer": 0},
    {"q": "What should you do in lightning?", "options": ["Stay inside", "Go outside", "Jump"], "answer": 0},
    {"q": "Which one is safe to drink?", "options": ["Water", "Oil", "Sand"], "answer": 0},
    {"q": "Which one gives us light at night?", "options": ["Moon", "Sun", "Cloud"], "answer": 0},
    {"q": "What should you wear when cold?", "options": ["Jacket", "Sunglasses", "Hat"], "answer": 0},
    {"q": "What comes from clouds and is wet?", "options": ["Rain", "Snow", "Sun"], "answer": 0},
    {"q": "What do you see in the sky at night?", "options": ["Stars", "Sun", "Rain"], "answer": 0},
    {"q": "Which one helps plants grow?", "options": ["Rain", "Fire", "Wind"], "answer": 0},
    {"q": "What should you not touch in storm?", "options": ["Lightning", "Umbrella", "Tree"], "answer": 0},
    {"q": "What can fly and is very colorful?", "options": ["Rainbow", "Cloud", "Sun"], "answer": 0},
    {"q": "What is round and hot in the sky?", "options": ["Sun", "Moon", "Cloud"], "answer": 0},
    {"q": "What can you wear to protect your head from sun?", "options": ["Hat", "Gloves", "Shoes"], "answer": 0},
    {"q": "What do we use to cover when raining?", "options": ["Umbrella", "Fan", "Sunglasses"], "answer": 0},
    {"q": "Which is wet and falls from clouds?", "options": ["Rain", "Snow", "Sand"], "answer": 0},
    {"q": "What makes a house shake sometimes?", "options": ["Earthquake", "Sun", "Rain"], "answer": 0},
    {"q": "What moves trees and hair on windy days?", "options": ["Wind", "Rain", "Sun"], "answer": 0},
    {"q": "What should you do when there is fire?", "options": ["Call for help", "Touch it", "Jump in it"], "answer": 0},   
]
# ---------------- MAIN LOOP ----------------
running = True
while running:
    clock.tick(FPS)

    # ---------------- EVENTS ----------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            dragging = True
            mouse_pos = event.pos

            # QUIZ ACTIVATION
            if quiz_icon_rect.collidepoint(mouse_pos) and not quiz_mode and not game_over:
                quiz_mode = True
                paused = True
                quiz_index = 0
                # pick 3 random questions each time
                quiz_questions = random.sample(all_quiz_questions, 3)

            # QUIZ OPTION CLICK
            if quiz_mode:
                option_height = 50
                q = quiz_questions[quiz_index]
                for i, option in enumerate(q["options"]):
                    option_rect = pygame.Rect(100, 160 + 80+ i * option_height, 800, 40)
                    if option_rect.collidepoint(mouse_pos):
                        if i == q["answer"]:
                            score += 100
                        quiz_index += 1
                        if quiz_index >= len(quiz_questions):
                            quiz_mode = False
                            paused = False
                            quiz_index = 0
                        break

        if event.type == pygame.MOUSEBUTTONUP:
            dragging = False

        if event.type == pygame.MOUSEMOTION and dragging and not quiz_mode:
            girl_x = event.pos[0]
            girl_x = max(0, min(WIDTH - 115, girl_x))

        # Game start / restart / pause / mute
        if event.type == pygame.MOUSEBUTTONDOWN:
            if waiting_for_click:
                waiting_for_click = False
                level += 1
                lightning_y = -100
                cyclone_y = -200
                earthquake_y = -300
                continue

            if game_over and not quiz_mode:
                restart_taps += 1
                if restart_taps >= 2:
                    game_over = False
                    game_started = True
                    restart_taps = 0
                    score = 0
                    level = 1
                    lives = 3
                    lightning_y = -100
                    cyclone_y = -200
                    earthquake_y = -300
                continue

            if not game_started:
                game_started = True
                score = 0
                level = 1
                lives = 3

            elif pause_rect.collidepoint(event.pos):
                paused = not paused

            elif mute_rect.collidepoint(event.pos):
                muted = not muted
                pygame.mixer.music.pause() if muted else pygame.mixer.music.unpause()

    # ---------------- BACKGROUND ----------------
    if level == 1:
        screen.blit(bg_img_level1, (0, 0))
    elif level == 2:
        screen.blit(bg_img_level2, (0, 0))
    else:
        screen.blit(bg_img_level3, (0, 0))

    # ---------------- TAP TO START ----------------
    if not game_started:
        blink_timer += 1
        if blink_timer > 30:
            blink_timer = 0
            show_text = not show_text
        if show_text:
            tap = big_font.render("Tap to Start", True, YELLOW)
            screen.blit(tap, tap.get_rect(center=(WIDTH//2, HEIGHT//2)))

    # ---------------- GAME LOGIC ----------------
    if game_started and not game_over and not paused and not waiting_for_click and not quiz_mode:
        speed_boost = level3_boost if level >= 3 else 0

        lightning_y += lightning_speed + speed_boost
        if lightning_y > HEIGHT:
            lightning_y = -100
            lightning_x = random.randint(50, WIDTH - 100)
            lightning_passed = False

        if level >= 2:
            cyclone_y += cyclone_speed + speed_boost
            if cyclone_y > HEIGHT:
                cyclone_y = -100
                cyclone_x = random.randint(50, WIDTH - 100)
                cyclone_passed = False

        if level >= 3:
            earthquake_y += earthquake_speed + speed_boost
            if earthquake_y > HEIGHT:
                earthquake_y = -200
                earthquake_x = random.randint(50, WIDTH - 120)
                earthquake_passed = False

        # ---------------- SCORE ----------------
        if not lightning_passed and lightning_y > girl_y:
            lightning_passed = True
            floating_points.append({'x': lightning_x, 'y': lightning_y, 'value': '+50', 'timer': 30})
            score += 50

        if level >= 2 and not cyclone_passed and cyclone_y > girl_y:
            cyclone_passed = True
            floating_points.append({'x': cyclone_x, 'y': cyclone_y, 'value': '+50', 'timer': 30})
            score += 50

        if level >= 3 and not earthquake_passed and earthquake_y > girl_y:
            earthquake_passed = True
            floating_points.append({'x': earthquake_x, 'y': earthquake_y, 'value': '+70', 'timer': 30})
            score += 70

        # ---------------- BEST SCORE ----------------
        if score > best_score:
            best_score = score
            with open("best_score.txt", "w") as f:
                f.write(str(best_score))
            new_high_score_popup_timer = new_high_score_popup_duration

        # ---------------- LEVEL UNLOCK ----------------
        if level == 1 and score >= 200:
            waiting_for_click = True
            level_message = ("Level 2 Unlocked!", "Tap to Continue")
        elif level == 2 and score >= 600:
            waiting_for_click = True
            level_message = ("Level 3 Unlocked!", "Tap to Continue")

        # ---------------- COLLISION ----------------
        girl_rect = pygame.Rect(girl_x, girl_y, 70, 70)
        lightning_rect = pygame.Rect(lightning_x, lightning_y, 60, 90)
        if girl_rect.colliderect(lightning_rect):
            lives -= 1
            lightning_y = -100
            if lives <= 0:
                game_over = True
                restart_taps = 0

        if level >= 2:
            cyclone_rect = pygame.Rect(cyclone_x, cyclone_y, 60, 60)
            if girl_rect.colliderect(cyclone_rect):
                lives -= 1
                cyclone_y = -200
                if lives <= 0:
                    game_over = True
                    restart_taps = 0

        if level >= 3:
            earthquake_rect = pygame.Rect(earthquake_x, earthquake_y, 110, 80)
            if girl_rect.colliderect(earthquake_rect):
                lives -= 1
                earthquake_y = -300
                if lives <= 0:
                    game_over = True
                    restart_taps = 0

    # ---------------- DRAW ----------------
    screen.blit(girl_img, (girl_x, girl_y))
    screen.blit(lightning_img, (lightning_x, lightning_y))
    if level >= 2:
        screen.blit(cyclone_img, (cyclone_x, cyclone_y))
    if level >= 3:
        screen.blit(earthquake_img, (earthquake_x, earthquake_y))

    # HEARTS
    for i in range(lives):
        screen.blit(heart_img, (WIDTH - 50 - i*40, 60))

    # FLOATING SCORE
    for fp in floating_points[:]:
        screen.blit(floating_font.render(fp['value'], True, YELLOW), (fp['x'], fp['y']))
        fp['y'] -= 1
        fp['timer'] -= 1
        if fp['timer'] <= 0:
            floating_points.remove(fp)

    # UI TEXT
    if level == 1:
        screen.blit(font.render(f"Score: {score}", True, DARK_PURPLE), (10, 10))
        screen.blit(font.render(f"Best: {best_score}", True, DARK_PURPLE), (10, 45))
        screen.blit(font.render(f"Level: {level}", True, DARK_PURPLE), (10, 80))
    else:
        screen.blit(font.render(f"Score: {score}", True, YELLOW), (10, 10))
        screen.blit(font.render(f"Best: {best_score}", True, WHITE), (10, 45))
        screen.blit(font.render(f"Level: {level}", True, LIGHT_BLUE), (10, 80))

    # QUIZ ICON ALWAYS
    screen.blit(quiz_icon_img, quiz_icon_rect)

    # Pause & Mute
    screen.blit(pause_img if not paused else play_img, pause_rect)
    screen.blit(mute_img if muted else unmute_img, mute_rect)

    # POPUPS
    if new_high_score_popup_timer > 0:
        popup_text = medium_font.render("NEW HIGHEST SCORE!", True, GREEN)
        screen.blit(popup_text, (WIDTH//2 - popup_text.get_width()//2, HEIGHT//2 - 100))
        new_high_score_popup_timer -= 1

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

    # ---------------- QUIZ DRAW ----------------
    if quiz_mode:
        pygame.draw.rect(screen, BLACK, (50, 150, 900, 400))
        pygame.draw.rect(screen, WHITE, (50, 150, 900, 400), 3)
        q = quiz_questions[quiz_index]
        question_text = big_font.render(q["q"], True, YELLOW)
        screen.blit(question_text, (60, 160))
        option_height = 50
        for i, option in enumerate(q["options"]):
            option_rect = pygame.Rect(100, 160 + 80 + i * option_height, 800, 40)
            pygame.draw.rect(screen, LIGHT_BLUE, option_rect)
            screen.blit(font.render(option, True, BLACK), (option_rect.x + 10, option_rect.y + 5))

    pygame.display.update()

pygame.quit()
sys.exit()
