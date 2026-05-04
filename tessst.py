import pygame
from fighter import Fighter
from button import Button

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

#game states

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

#number of frames per actions
player1_animation_steps = [19, 8, 10, 8, 13, 10, 8, 13, 9, 27, 7, 8, 21, 10]
player2_animation_steps = player1_animation_steps

#load spritesheet / text / image
player1_sheet = pygame.image.load("assets/sprites/sora sprite sheet.png")
player2_sheet = pygame.image.load("assets/sprites/sora sprite sheet_2.png")

text = pygame.font.SysFont("Wide Latin", 31) #text font and size
count_text = pygame.font.SysFont("Wide Latin", 100) #counter text

crown_img = pygame.image.load("assets/image/round_crown.png").convert_alpha()
bg_image = pygame.image.load("assets/image/destiny-islandss.jpg").convert_alpha()
player_names = pygame.image.load("assets/image/player names.png").convert_alpha()
player1_win = pygame.image.load("assets/image/player1 WINS.png")
player2_win = pygame.image.load("assets/image/player2 WINS.png")
play_img = pygame.image.load("assets/image/play_button.png")
help_img = pygame.image.load("assets/image/help_button.png")
back_img = pygame.image.load("assets/image/back_button.png")
quit_img = pygame.image.load("assets/image/quit_button.png")
leave_img = pygame.image.load("assets/image/leave_button.png")

#button instances
play_button = Button(0,0, play_img, 1)
help_button = Button(0,0, help_img, 1)
back_button = Button(0,0, back_img, 1)
quit_button = Button(0,0, quit_img, 1)
leave_button = Button(0,0, leave_img, 1)


def draw_names():
    scaled_name = pygame.transform.scale(player_names, (SCREEN_WIDTH, SCREEN_HEIGHT))
    round_count = screen.blit(scaled_name, (3, -16))

def draw_text():
    counter = count_text.render(str(intro_count-1), True, WHITE)
    counter_postion = screen.blit(counter, (490, SCREEN_HEIGHT/4))

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

#create 2 instances of fighters
fighter_1 = Fighter(1, 200, 310, False, player1_data, player1_sheet, player1_animation_steps) #note that fighter class is 155 wide and 260 tall so +-155 on the x position
fighter_2 = Fighter(2, 700, 310, True, player2_data, player2_sheet, player2_animation_steps)

#GAME LOOP
run = True
while run:

    clock.tick(FPS)

    draw_bg()

    draw_health_bar(fighter_1.health, 20, 20) #width of hp is 400 from def draw_health_bar(health, x, y):
    draw_health_bar(fighter_2.health, 660, 20)
    #player name text/image
    draw_names()

    #draws number of wins per round
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
        fighter_1.move (SCREEN_WIDTH, screen, fighter_2, round_over)
        fighter_2.move (SCREEN_WIDTH, screen, fighter_1, round_over)

    else:
        draw_text()
        #update count timer
        if(pygame.time.get_ticks() - last_count_update) >= 1000:
            intro_count -= 1
            last_count_update = pygame.time.get_ticks()
    

    pygame.draw.line(screen, WHITE, (SCREEN_WIDTH/2, 0), (SCREEN_WIDTH/2, 720), 1) #center line

    #update fighters
    fighter_1.update(fighter_2)
    fighter_2.update(fighter_1)

    fighter_1.draw(screen)
    fighter_2.draw(screen)
    
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
                fighter_1 = Fighter(1, 200, 310, False, player1_data, player1_sheet, player1_animation_steps) 
                fighter_2 = Fighter(2, 700, 310, True, player2_data, player2_sheet, player2_animation_steps)

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:

                pass #pause event here
            
        if event.type == pygame.QUIT:
            run = False
    
    pygame.display.update()

pygame.quit()
