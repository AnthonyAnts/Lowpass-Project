import pygame
from fighter import Fighter
from button import Button
from pygame import mixer

pygame.init()

SCREEN_WIDTH=1080
SCREEN_HEIGHT=620

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Coast Pyter")

clock = pygame.time.Clock()
FPS = 60

RED = (255, 0, 0)
YELLOW = (255, 235, 0)
WHITE = (255, 255, 255)

#define game state variables
game_paused = False

#define game variables
intro_count = 4
last_count_update = pygame.time.get_ticks()
score = [0,0] #[P1, P2]
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

#load images
text = pygame.font.SysFont("Wide Latin", 31) #text font and size
count_text = pygame.font.SysFont("Wide Latin", 100) #counter text
crown_img = pygame.image.load("assets/image/round_crown.png").convert_alpha()
bg_image = pygame.image.load("assets/image/destiny-islandss.jpg").convert_alpha()
player_names = pygame.image.load("assets/image/player names.png").convert_alpha()
player1_win = pygame.image.load("assets/image/player1 WINS.png")
player2_win = pygame.image.load("assets/image/player2 WINS.png")
resume_img = pygame.image.load("assets/image/play_button.png").convert_alpha()

#load sounds
pygame.mixer.music.load("assets/sound/Kingdom Hearts 1.5 OST Destiny Islands Battle Theme ( Bustin' Up on the Beach ).mp3")
pygame.mixer.music.set_volume(0.20)
pygame.mixer.music.play(-1, 0.0, 5000)
standing_light_sfx = pygame.mixer.Sound("assets/sound/attack/light attack/se02001#18.wav")
standing_light_sfx.set_volume(0.5)
standing_heavy_sfx = pygame.mixer.Sound("assets/sound/attack/heavy attack/se02001#07.wav")
standing_heavy_sfx.set_volume(0.5)
crouching_light_sfx = pygame.mixer.Sound("assets/sound/attack/light attack/se02001#19.wav")
crouching_light_sfx.set_volume(0.5)
crouching_heavy_sfx = pygame.mixer.Sound("assets/sound/attack/heavy attack/se02001#04.wav")
crouching_heavy_sfx.set_volume(0.5)
hurt_sfx = pygame.mixer.Sound("assets/sound/hurt/Battle-Sora#028.wav")
hurt_sfx.set_volume(0.5)
victory_sfx = pygame.mixer.Sound("assets/sound/victory/fd_po_chat_sora_random6_000.wav")
victory_sfx.set_volume(0.5)

#create button instance
resume_button = Button(0, 0, resume_img, 1)

player_animation_steps = { # lower speed value = faster, higher speed value = slower, how it works: frame division, 60 frames/2 = 30, runs at 30 fps
    "idle": {"frames": 19, "speed": 4},
    "walk": {"frames": 8, "speed": 3},
    "walk_back": {"frames": 10, "speed": 6},
    "standing_light": {
        "frames": 8,
        "startup": 3, # To make it faster: lower startup and/or recovery. To make it slower, increase startup/recovery.
        "active": 3, # remember, we're running at 60 fps so if you're counting sprites, divide 60 by the tally
        "recovery": 2,
        "hitbox": {
            "width_multiplier": 1.3,
            "height_multiplier": 1.0,
        },
        "on_hit": {
            "damage": 15,
            "stun": 13,
            "knockback": 90,
        },
        "on_block": {
            "stun": 5,
            "knockback": 50
        },
        "on_target_block": {
            "stun": 10,
            "knockback": 50
        },
        "gatling": ["standing_heavy", "crouching_heavy"],
    },

    "standing_heavy": {
        "frames": 15,
        "startup": 6,
        "active": 4,
        "recovery": 18,
        "hitbox": {
            "width_multiplier": 2.0,
            "height_multiplier": 1.0,
        },
        "on_hit": { 
            "damage": 30,
            "stun": 20,
            "knockback": 100,
        }, 
        "on_block": {
            "stun": 12,
            "knockback": 50
        },
        "on_target_block": {
            "stun": 30,
            "knockback": 50
        },
    },

    "crouch": {"frames": 10},

    "crouching_light": {
        "frames": 8,
        "startup": 3,
        "active": 3,
        "recovery": 3,
        "hitbox": {
            "width_multiplier": 0.9,
            "height_multiplier": 1.0,
        },
        "on_hit": {
            "damage": 10,
            "stun": 12,
            "knockback": 90,
        }, 
        "on_block": {
            "stun": 10,
            "knockback": 50
        }, 
        "on_target_block": {
            "stun": 10,
            "knockback": 50
        },
        "gatling": ["standing_heavy", "crouching_heavy"],
    },

    "crouching_heavy": {
        "frames": 13,
        "startup": 4,
        "active": 4,
        "recovery": 20,
        "hitbox": {
            "width_multiplier": 2.0,
            "height_multiplier": 1, 
        },
        "on_hit": {
            "damage": 30,
            "stun": 18,
            "knockback": 100,
        },
        "on_block": {
            "stun": 15,
            "knockback": 50
        },
        "on_target_block": {
            "stun": 15,
            "knockback": 50
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
        "alpha": 150
        },
    "standing_heavy_vfx": {
        "frames": 16, 
        "speed": 4, 
        "x_offset": 26, 
        "y_offset": 0.5,
        "alpha": 225
        },
    "crouching_light_vfx": {
        "frames": 8, 
        "speed": 4, 
        "x_offset": 20, 
        "y_offset": 1.0,
        "alpha": 200
        },
    "crouching_heavy_vfx": {
        "frames": 13, 
        "speed": 4, 
        "x_offset": 20, 
        "y_offset": 10,
        "alpha": 150
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


def draw_names():
    scaled_name = pygame.transform.scale(player_names, (SCREEN_WIDTH, SCREEN_HEIGHT))
    round_count = screen.blit(scaled_name, (3, -16))

def draw_text():
    counter = count_text.render(str(intro_count-1), True, WHITE)
    counter_postion = screen.blit(counter, (500, SCREEN_HEIGHT/4))

def draw_bg():
    scaled_bg = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled_bg, (0,0))

def draw_crown1(x):
    scaled_crown = pygame.transform.scale(crown_img, (130, 100))
    round_count = screen.blit(scaled_crown, (x,20))

def draw_crown2(x1, x2):
    scaled_crown = pygame.transform.scale(crown_img, (130, 100))
    round_count = screen.blit(scaled_crown, (x1, 20))
    round_count = screen.blit(scaled_crown, (x2, 20))   

def draw_player_win(N):
    scaled_win1 = pygame.transform.scale(player1_win, (SCREEN_WIDTH, SCREEN_HEIGHT))
    scaled_win2 = pygame.transform.scale(player2_win, (SCREEN_WIDTH, SCREEN_HEIGHT))
    if N == 1:
        game_win1 = screen.blit(scaled_win1, (10, 10))
    if N == 2:
        game_win2 = screen.blit(scaled_win2, (10, 10))

#HP bar
def draw_health_bar(health, x, y):
    ratio = health / 100
    pygame.draw.rect(screen, WHITE, (x - 3, y - 3, 406, 36))
    pygame.draw.rect(screen, RED, (x, y, 400, 30))
    pygame.draw.rect(screen, YELLOW, (x, y, 400 * ratio, 30))

fighter_1 = Fighter(1, 200, 310, False, player1_data, player1_sheet, player_animation_steps, vfx_sheet, vfx_animation_steps)
fighter_2 = Fighter(2, 700, 310, True, player2_data, player2_sheet, player2_animation_steps, vfx_sheet, vfx_animation_steps)

vfx_group = pygame.sprite.Group()    
    #GAME LOOP
run = True
while run:
    clock.tick(FPS)

    draw_bg()
    
    draw_health_bar(fighter_1.health, 20, 20) #width of hp is 400 from def draw_health_bar(health, x, y):
    draw_health_bar(fighter_2.health, 660, 20)

    if score[0] == 1:
        draw_crown1(270)
    if score[0] == 2:
        draw_crown2(270, 330)
    if score[1] == 1:
        draw_crown1(620)
    if score[1] == 2:
        draw_crown2(620, 670)

    if intro_count <= 1:
        #move fighters
        fighter_1.move (SCREEN_WIDTH, screen, fighter_2, round_over, vfx_group)
        fighter_2.move (SCREEN_WIDTH, screen, fighter_1, round_over, vfx_group)

    else:
        draw_text()
        #update count timer
        if(pygame.time.get_ticks() - last_count_update) >= 1000:
            intro_count -= 1
            last_count_update = pygame.time.get_ticks()

    #player name text/image
    draw_names()

    #update fighters
    fighter_1.update(fighter_2)
    fighter_2.update(fighter_1)
    # update vfx
    vfx_group.update()

    fighter_1.draw(screen)
    fighter_2.draw(screen)
    # drawing vfx
    vfx_group.draw(screen)

    if score [0] == 2:
        draw_player_win(1)
    elif score [1] == 2: 
        draw_player_win(2)
    else:
        #check for player defeat
        if round_over == False:
            if fighter_1.alive == False:
                score [1] += 1
                round_over = True
                round_over_time = pygame.time.get_ticks()
            elif fighter_2.alive == False:
                score [0] += 1
                round_over = True
                round_over_time = pygame.time.get_ticks()
        else:
            if pygame.time.get_ticks() - round_over_time > round_over_cooldown:
                round_over = False
                intro_count = 4
                fighter_1 = Fighter(1, 200, 310, False, player1_data, player1_sheet, player_animation_steps, vfx_sheet, vfx_animation_steps) #note that fighter class is 155 wide and 260 tall so +-155 on the x position
                fighter_2 = Fighter(2, 700, 310, True, player2_data, player2_sheet, player2_animation_steps, vfx_sheet, vfx_animation_steps)
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game_paused = True
            
        if event.type == pygame.QUIT:
            run = False
    
    pygame.display.update()

pygame.quit()

