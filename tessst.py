import pygame
from fighter import Fighter
from button import Button

pygame.init()

SCREEN_WIDTH=1080
SCREEN_HEIGHT=620

STATE_MENU = "menu"
STATE_RUN = "run"
STATE_PAUSE = "pause"
STATE_HELP = "help"
STATE_GAME_OVER = "game_over"
GAME_STATE = STATE_MENU

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Coast Pyter")

clock = pygame.time.Clock()
FPS = 60

RED = (255, 0, 0)
YELLOW = (255, 235, 0)
WHITE = (255, 255, 255)

#define game variables
intro_count = 3
last_count_update = pygame.time.get_ticks()
score = [0,0] #[P1, P2]
streak = [0,0]
round_winner = 0
match_winner = 0
round_over = False
round_over_cooldown = 2000

#define fighter variables
player1_size = 120
player1_scale = 5
player1_offset = [44, 68] #trial and error
player1_data = [player1_size, player1_scale, player1_offset]

player2_size = 120
player2_scale = 5
player2_offset = [45, 68]
player2_data = [player2_size, player2_scale, player2_offset]

#load spritesheet
player1_sheet = pygame.image.load("assets/sprites/sora sprite sheet.png")
player2_sheet = pygame.image.load("assets/sprites/sora sprite sheet_2.png")
vfx_sheet = pygame.image.load("assets/sprites/vfx sprite sheet.png").convert_alpha()

p1_controls = {
    'left': pygame.K_a, 'right': pygame.K_d, 'down': pygame.K_s,
    'light': pygame.K_j, 'heavy': pygame.K_k
}
p2_controls = {
    'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'down': pygame.K_DOWN,
    'light': pygame.K_KP_2, 'heavy': pygame.K_KP_3
}

player_animation_steps = { # lower speed value = faster, higher speed value = slower, how it works: frame division, 60 frames/2 = 30, runs at 30 fps
    "idle": {"frames": 19, "speed": 4},
    "walk": {"frames": 8, "speed": 8},
    "walk_back": {"frames": 10, "speed": 6},
    "standing_light": {
        "frames": 8,
        "startup": 4, # To make it faster: lower startup and/or recovery. To make it slower, increase startup/recovery.
        "active": 6, # remember, we're running at 60 fps so if you're counting sprites, divide 60 by the tally
        "recovery": 10,
        "hitbox": {
            "width_multiplier": 1.3,
            "height_multiplier": 1.0,
        },
        "on_hit": {
            "damage": 100,
            "stun": 12,
            "knockback": 12,
        },
        "on_block": {
            "stun": 5,
            "knockback": 10
        },
        "on_target_block": {
            "stun": 10,
            "knockback": 10
        },
        "gatling": ["standing_heavy", "crouching_heavy"],
    },

    "standing_heavy": {
        "frames": 13,
        "startup": 4,
        "active": 4,
        "recovery": 30,
        "hitbox": {
            "width_multiplier": 2.0,
            "height_multiplier": 1.0,
        },
        "on_hit": { 
            "damage": 30,
            "stun": 20,
            "knockback": 20,
        }, 
        "on_block": {
            "stun": 12,
            "knockback": 15
        },
        "on_target_block": {
            "stun": 30,
            "knockback": 20
        },
    },

    "crouch": {"frames": 10},

    "crouching_light": {
        "frames": 8,
        "startup": 4,
        "active": 4,
        "recovery": 10,
        "hitbox": {
            "width_multiplier": 0.9,
            "height_multiplier": 1.0,
        },
        "on_hit": {
            "damage": 10,
            "stun": 12,
            "knockback": 12,
        }, 
        "on_block": {
            "stun": 10,
            "knockback": 10
        }, 
        "on_target_block": {
            "stun": 10,
            "knockback": 5
        },
        "gatling": ["standing_heavy", "crouching_heavy"],
    },

    "crouching_heavy": {
        "frames": 13,
        "startup": 10,
        "active": 6,
        "recovery": 12,
        "hitbox": {
            "width_multiplier": 2.0,
            "height_multiplier": 0.5, 
        },
        "on_hit": {
            "damage": 30,
            "stun": 18,
            "knockback": 18,
        },
        "on_block": {
            "stun": 15,
            "knockback": 12
        },
        "on_target_block": {
            "stun": 15,
            "knockback": 5
        },
    },
    "hurt": {"frames": 8, "speed": 4},
    "victory": {"frames": 27, "speed": 4},
    "defeat": {"frames": 7, "speed": 20,},
}

vfx_animation_steps = { 
    "standing_light_vfx": {
        "frames": 8, 
        "speed": 4, 
        "x_offset": 40, 
        "y_offset": 15,
        "alpha": 100
        },
    "standing_heavy_vfx": {
        "frames": 15, 
        "speed": 4, 
        "x_offset": 30, 
        "y_offset": 0.5,
        "alpha": 155
        },
    "crouching_light_vfx": {
        "frames": 8, 
        "speed": 4, 
        "x_offset": 20, 
        "y_offset": 1.0,
        "alpha": 100
        },
    "crouching_heavy_vfx": {
        "frames": 13, 
        "speed": 4, 
        "x_offset": 20, 
        "y_offset": 10,
        "alpha": 100
        },
    "block": {
        "frames": 4, 
        "speed": 4, 
        "x_offset": 26, 
        "y_offset": 30,
        "alpha": 100
        }
}

player2_animation_steps = player_animation_steps


menu_font = pygame.font.SysFont("Wide Latin", 60)
text = pygame.font.SysFont("Wide Latin", 31) #text font and size
count_text = pygame.font.SysFont("Wide Latin", 100) #counter text
crown_img = pygame.image.load("assets/image/round_crown.png").convert_alpha()
play_img = pygame.image.load("assets/image/play_button.png")
back_img = pygame.image.load("assets/image/back_button.png")
help_button_img = pygame.image.load("assets/image/help_button.png")
help_img = pygame.image.load("assets/image/help.png")
quit_img = pygame.image.load("assets/image/quit_button.png")
leave_img = pygame.image.load("assets/image/leave_button.png")
resume_img = pygame.image.load("assets/image/resume_button.png")
rematch_img = pygame.image.load("assets/image/rematch_button.png")
# i_love_snake_case

play_button = Button(0, 0, play_img, 1, hitbox=(350, 110, 380, 80))
back_button = Button(0, 0, back_img, 1, hitbox = (0, 0, 100, 80))
help_button = Button(0, 0, help_button_img, 1, hitbox = (350, 270, 380, 80))
leave_button = Button(0, 0, leave_img, 1, hitbox = (350, 420, 380, 80))
resume_button = Button(0, 0, resume_img, 1, hitbox = (350, 110, 380, 80))
quit_button = Button(0, 0, quit_img, 1, hitbox = (350, 420, 380, 80))
rematch_button = Button(0, 0, rematch_img, 1, hitbox = (350, 270, 380, 80))

bg_image = pygame.image.load("assets/image/destiny-islandss.jpg").convert_alpha()
player_names = pygame.image.load("assets/image/player names.png").convert_alpha()
player1_win = pygame.image.load("assets/image/player1 WINS.png")
player2_win = pygame.image.load("assets/image/player2 WINS.png")

def draw_menu(surface):
    title = menu_font.render("COAST PYTER", True, WHITE)
    surface.blit(title, (130, 20))

def draw_pause(surface):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    surface.blit(overlay, (0, 0))
    paused = menu_font.render("PAUSED", True, WHITE)
    surface.blit(paused, (300, 20))

def draw_game_over(surface, winner):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(220)
    overlay.fill((0, 0, 0))

    surface.blit(overlay, (0, 0))
    if winner == 1:
        draw_victory(surface, winner)
    else: 
        draw_victory(surface, winner)

def draw_bg(surface):
    surface.blit(pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0,0))

def draw_names(surface):
    surface.blit(pygame.transform.scale(player_names, (SCREEN_WIDTH, SCREEN_HEIGHT)), (3, -16))

def draw_countdown(surface, count):
    counter = count_text.render(str(count), True, WHITE)
    surface.blit(counter, (480, SCREEN_HEIGHT/4))

def draw_crowns(surface, score_p1, score_p2):
    scaled_crown = pygame.transform.scale(crown_img, (130, 100))
    if score_p1 >= 1: surface.blit(scaled_crown, (270, 20))
    if score_p1 == 2: surface.blit(scaled_crown, (330, 20))
    if score_p2 >= 1: surface.blit(scaled_crown, (620, 20))
    if score_p2 == 2: surface.blit(scaled_crown, (670, 20))

def draw_health_bar(surface, health, x, y):
    ratio = max(health / 100.0, 0) # Prevent negative health bars
    pygame.draw.rect(surface, WHITE, (x - 3, y - 3, 406, 36))
    pygame.draw.rect(surface, RED, (x, y, 400, 30))
    pygame.draw.rect(surface, YELLOW, (x, y, 400 * ratio, 30))

def draw_victory(surface, player_num):
    img = player1_win if player_num == 1 else player2_win
    surface.blit(pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT)), (10, -100))

def draw_streaks(surface):
    if streak[0] > 0:
        p1_streak_txt = text.render(f"Wins: {streak[0]}", True, WHITE)
        surface.blit(p1_streak_txt, (25, 90))
    if streak[1] > 0:
        p2_streak_txt = text.render(f"Wins: {streak[1]}", True, WHITE)
        surface.blit(p2_streak_txt, (865, 90))


def reset_round():
    f1 = Fighter(1, 200, 310, False, player1_data, player1_sheet, player_animation_steps, vfx_sheet, vfx_animation_steps, p1_controls)
    f2 = Fighter(2, 700, 310, True, player2_data, player2_sheet, player2_animation_steps, vfx_sheet, vfx_animation_steps, p2_controls)
    return f1, f2, pygame.sprite.Group()

score = [0, 0]
intro_count = 3
last_count_update = pygame.time.get_ticks()
round_over = False
round_over_cooldown = 2000
click_cooldown = 0

fighter_1, fighter_2, vfx_group = reset_round()

run = True
while run:
    # I'M LAZY SO I'M PUTTING A CLICK COOLDOWN FOR LEAVE AND QUIT
    if click_cooldown > 0:
        click_cooldown -= 1
    clock.tick(FPS)
    screen.fill((0,0,0))

    # events only - keyboard inputs only
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        elif event.type == pygame.KEYDOWN:
            if GAME_STATE == STATE_RUN:
                if event.key == pygame.K_ESCAPE:
                    GAME_STATE = STATE_PAUSE

            elif GAME_STATE == STATE_PAUSE:
                if event.key == pygame.K_ESCAPE:
                    GAME_STATE = STATE_RUN

            elif GAME_STATE == STATE_HELP:
                if event.key == pygame.K_ESCAPE:
                    GAME_STATE = previous_state


    # MENU
    if GAME_STATE == STATE_MENU:
        draw_bg(screen)
        draw_menu(screen)
        print(click_cooldown)
        if play_button.draw(screen):
            fighter_1, fighter_2, vfx_group = reset_round()
            score = [0,0]
            into_count = 3
            GAME_STATE = STATE_RUN

        if help_button.draw(screen):
            previous_state = STATE_MENU
            GAME_STATE = STATE_HELP

        if quit_button.draw(screen) and click_cooldown == 0:
            run = False

    elif GAME_STATE == STATE_HELP:
        screen.blit(help_img, (0, 0))
        
        if back_button.draw(screen):
            GAME_STATE = previous_state

    # RUN
    elif GAME_STATE == STATE_RUN:
        draw_bg(screen)
        draw_health_bar(screen, fighter_1.health, 20, 20)
        draw_health_bar(screen, fighter_2.health, 660, 20)
        draw_crowns(screen, score[0], score[1])
        draw_names(screen)
        draw_streaks(screen)

        # COUNTDOWN
        if intro_count > 0:
            draw_countdown(screen, intro_count)

            if (pygame.time.get_ticks() - last_count_update) >= 1000:
                intro_count -= 1
                last_count_update = pygame.time.get_ticks()

        else:
            fighter_1.move(SCREEN_WIDTH, fighter_2, round_over, vfx_group)
            fighter_2.move(SCREEN_WIDTH, fighter_1, round_over, vfx_group)

        fighter_1.update(fighter_2)
        fighter_2.update(fighter_1)
        vfx_group.update()
        fighter_1.draw(screen)
        fighter_2.draw(screen)
        vfx_group.draw(screen)

        if not round_over:

            if not fighter_1.alive:
                score[1] += 1
                round_winner = 2
                round_over = True
                round_over_time = pygame.time.get_ticks()

            elif not fighter_2.alive:
                score[0] += 1
                round_winner = 1
                round_over = True
                round_over_time = pygame.time.get_ticks()

        else:
            draw_victory(screen, round_winner)

            if pygame.time.get_ticks() - round_over_time > round_over_cooldown:

                if score[0] >= 2:
                    match_winner = 1
                    streak[0] += 1
                    streak[1] = 0
                    GAME_STATE = STATE_GAME_OVER

                elif score[1] >= 2:
                    match_winner = 2
                    streak[0] = 0
                    streak[1] += 1
                    GAME_STATE = STATE_GAME_OVER

                else:
                    round_over = False
                    intro_count = 3
                    fighter_1, fighter_2, vfx_group = reset_round()

    elif GAME_STATE == STATE_PAUSE:

            draw_bg(screen)

            fighter_1.draw(screen)
            fighter_2.draw(screen)
            vfx_group.draw(screen)

            draw_pause(screen)

            if resume_button.draw(screen):
                GAME_STATE = STATE_RUN

            if help_button.draw(screen):
                previous_state = STATE_PAUSE
                GAME_STATE = STATE_HELP

            if leave_button.draw(screen):
                GAME_STATE = STATE_MENU
                click_cooldown = 20
    
    # game over
    elif GAME_STATE == STATE_GAME_OVER:
        draw_bg(screen)

        fighter_1.draw(screen)
        fighter_2.draw(screen)
        vfx_group.draw(screen)

        draw_game_over(screen, match_winner)

        if rematch_button.draw(screen):   # rematch button ideally
            fighter_1, fighter_2, vfx_group = reset_round()
            score = [0, 0]
            intro_count = 3
            round_over = False
            GAME_STATE = STATE_RUN

        if leave_button.draw(screen):
            GAME_STATE = STATE_MENU
            click_cooldown = 20

    pygame.display.update()

pygame.quit()


