import pygame

class Button():
    def __init__(self, x, y, image, scale=1, hitbox=None):
        width = image.get_width()
        height = image.get_height()
        self.base_image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(topleft=(x,y))
        # dirty implementation to uh, keep our predefined buttons in place
        self.draw_x = x
        self.draw_y = y
        self.clicked = False

        
        if hitbox:
            self.rect = pygame.Rect(hitbox)
        else:
            self.rect= self.image.get_rect(topleft=(x, y))

    def draw(self, surface):
        action = False
        #get mouse position
        pos = pygame.mouse.get_pos()
        self.image = self.base_image.copy()

        #check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            hover_image = self.base_image.copy()
            hover_image.set_alpha(180)
            self.image = hover_image

            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True
        
        else:
            self.image.set_alpha(255)
        
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        surface.blit(self.image, (self.draw_x, self.draw_y))
        # pygame.draw.rect(surface, (255, 0, 0), self.rect, 2) # <-- DEBUG FOR HITBOX

        return action
     #38 x 58
