import pygame
from fighter import Fighter

pygame.init()

SCREEN_WIDTH=1080
SCREEN_HEIGHT=620

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Coast Pyter")

clock = pygame.time.Clock()
FPS = 60

RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)

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

player1_animation_steps = [19, 8, 10, 8, 21, 10, 8, 13, 9, 27, 7]
player2_animation_steps = player1_animation_steps

text = pygame.font.SysFont("Wide Latin", 31) #text font and size
count_text = pygame.font.SysFont("Wide Latin", 100) #counter text
count_text = pygame.font.SysFont("Wide Latin", 100) #counter text
score_text = pygame.font.SysFont("Wide Latin", 20) #score text


bg_image = pygame.image.load("assets/image/destiny-islandss.jpg").convert_alpha()

def draw_text():
    counter = count_text.render(str(intro_count-1), True, WHITE)
    counter_postion = screen.blit(counter, (480, SCREEN_HEIGHT/4))

def draw_bg():
    scaled_bg = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled_bg, (0,0))

#HP bar
def draw_health_bar(health, x, y):
    ratio = health / 100
    pygame.draw.rect(screen, WHITE, (x - 3, y - 3, 406, 36))
    pygame.draw.rect(screen, RED, (x, y, 400, 30))
    pygame.draw.rect(screen, YELLOW, (x, y, 400 * ratio, 30))


#create 2 instances of fighters
fighter_1 = Fighter(1, 200, 310, False, player1_data, player1_sheet, player1_animation_steps) #note that fighter class is 155 wide and 260 tall so +-155 on the x position
fighter_2 = Fighter(2, 700, 310, True, player2_data, player1_sheet, player2_animation_steps)

#GAME LOOP
run = True
while run:

    clock.tick(FPS)

    draw_bg()

    draw_health_bar(fighter_1.health, 20, 20) #width of hp is 400 from def draw_health_bar(health, x, y):
    draw_health_bar(fighter_2.health, 660, 20)
    screen.blit(score_text.render("P1:  "+ str(score[0]), True, RED), (335, 55))
    screen.blit(score_text.render("P2:  "+ str(score[1]), True, RED), (660, 55))

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

    #player name text/image
    player1_text = text.render("Player 1", True, WHITE) #text to show player 1 name
    textPosition = screen.blit(player1_text, (20, 55))
    player2_text = text.render("Player 2", True, WHITE) #text to show player 2 name
    textPosition = screen.blit(player2_text, (838, 55))

    #update fighters
    fighter_1.update(fighter_2)
    fighter_2.update(fighter_1)

    fighter_1.draw(screen)
    fighter_2.draw(screen)

    
    
    if score == [2,0]:
        player_text = text.render("Player 1 Wins!", True, WHITE) #text to show player 1 name
        textPosition = screen.blit(player_text, (SCREEN_WIDTH/3, SCREEN_HEIGHT/3))
        
    elif score == [0,2]:
        player_text = text.render("Player 2 Wins!", True, WHITE) #text to show player 1 name
        textPosition = screen.blit(SCREEN_WIDTH/3, SCREEN_HEIGHT/3)  
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
            screen.blit(player1_text, (500, 300))
            if pygame.time.get_ticks() - round_over_time > round_over_cooldown:
                round_over = False
                intro_count = 4
                fighter_1 = Fighter(1, 200, 310, False, player1_data, player1_sheet, player1_animation_steps) 
                fighter_2 = Fighter(2, 700, 310, True, player2_data, player1_sheet, player2_animation_steps)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    
    pygame.display.update()

pygame.quit()
