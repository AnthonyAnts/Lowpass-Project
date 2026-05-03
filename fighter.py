import pygame
import time

class Fighter():
    def __init__(self, player, x, y, flip, data, sprite_sheet, animation_steps):
        self.player = player
        self.size = data[0]
        self.image_scale = data[1]
        self.offset = data[2]
        self.flip = flip
        self.animation_list = self.load_images(sprite_sheet, animation_steps)
        self.action = 0 #0:idle 1:running 2: walking back 3:s.L 4:s.H 5:crouching 6:c.L 7:c.H 8:Hurt 9:Victory 10:Defeat
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index]
        self.update_time = pygame.time.get_ticks()
        self.rect = pygame.Rect((x, y, 155, 260)) #hurtbox
        self.walking = False
        self.walking_back = False
        self.crouching = False
        self.attacking = False
        self.attack_type = 0
        self.attack_cooldown = 0 #this is where frame data comes in
        self.hit = False 
        self.health = 100
        self.alive = True
        self.block = False
        self.victory = False
        self.knockback_distance = 0
        self.knockback_cooldown = 0 # recovery frames i guess

#animation
    def load_images(self, sprite_sheet, animation_steps):
        animation_list = []
        for y, animation in enumerate(animation_steps):
            temp_img_list = []    
            for x in range(animation):
                temp_img = sprite_sheet.subsurface(x * self.size, y * self.size , self.size, self.size)
                temp_img_list.append(pygame.transform.scale(temp_img, (self.size * self.image_scale, self.size * self.image_scale)))
            animation_list.append(temp_img_list)
        return animation_list

#movement
    def move(self, screen_width, surface, target, round_over):
        self.SPEED = 20 #trial and error walking speed
        self.dx = 0    
        self.walking = False
        self.walking_back = False
        self.crouching = False
        self.block = False
        self.attack_type = 0
    
        key = pygame.key.get_pressed()
        ki = pygame.KEYDOWN

        if self.knockback_cooldown > 0:
            # 1 second knockback
            self.knockback_cooldown -= 1
            self.dx = self.knockback_distance 

        #can only move when not attacking
        if self.attacking == False and self.alive == True and round_over == False:
            if self.player == 1:   
            #movement
                if key[pygame.K_a]:
                    self.dx = -self.SPEED + 10 #walking back speed
                    self.walking_back = True
                    self.block = True
                if key[pygame.K_d]:
                    self.dx = self.SPEED
                    self.walking = True
                if key[pygame.K_s]:
                    self.dx = 0
                    self.crouching = True
               
                #attack
                #c.L
                if key[pygame.K_j] and key[pygame.K_s]:
                    self.c_L_attack(surface, target)
                    self.attack_type = 3
                #c.H        
                elif key[pygame.K_k] and key[pygame.K_s]:
                    self.c_H_attack(surface, target)
                    self.attack_type = 4
                #s.L
                elif key[pygame.K_j]:
                    self.s_L_attack(surface, target)
                    self.attack_type = 1
                #s.H         
                elif key[pygame.K_k]:
                    self.s_H_attack(surface, target)
                    self.attack_type = 2

            #check player 2 control
            if self.player == 2:   
            #movement
                if key[pygame.K_LEFT]:
                    self.dx = -self.SPEED + 10 #walking back speed
                    self.walking_back = True
                    self.block = True
                if key[pygame.K_RIGHT]:
                    self.dx = self.SPEED
                    self.walking = True
                
                if key[pygame.K_DOWN]:
                    self.dx = 0
                    self.crouching = True
               
                #attack
                #c.L
                if key[pygame.K_KP_2] and key[pygame.K_DOWN]:
                    self.c_L_attack(surface, target)
                    self.attack_type = 3
                #c.H        
                elif key[pygame.K_KP_3] and key[pygame.K_DOWN]:
                    self.c_H_attack(surface, target)
                    self.attack_type = 4
                #s.L
                elif key[pygame.K_KP_2]:
                    self.s_L_attack(surface, target)
                    self.attack_type = 1
                #s.H         
                elif key[pygame.K_KP_3]:
                    self.s_H_attack(surface, target)
                    self.attack_type = 2


        #wall limit
        if self.rect.left + self.dx < 0:
            self.dx = -self.rect.left
        if self.rect.right + self.dx > screen_width:
            self.dx = screen_width - self.rect.right
        
        # collision 
        player_border = self.rect.move(self.dx, 0)
        if player_border.colliderect(target.rect):
            self.dx = 0
        
        #flip to face each other (for player 2 flip)
        if target.rect.centerx > self.rect.centerx:
            self.flip = False
        else:
            self.flip = True

        #apply attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        #update player position
        self.rect.x += self.dx

    def apply_knockback(self, attacker, attack_type):
        self.knockback_distance = 0
        self.knockback_cooldown = 5
        # Knockback logic
        if attack_type == 1: # Standing Light
            if self.rect.centerx > attacker.rect.centerx:
                direction = 1
            else:
                direction = -1
            self.knockback_distance = direction * 10
        elif attack_type == 2: # Standing Heavy
            if self.rect.centerx > attacker.rect.centerx:
                direction = 1
            else:
                direction = -1
            self.knockback_distance = direction * 12
        elif attack_type == 3: # Crouching Light
            if self.rect.centerx > attacker.rect.centerx:
                direction = 1
            else:
                direction = -1
            self.knockback_distance = direction * 10 
        elif attack_type == 4: # Crouching Heavy
            if self.rect.centerx > attacker.rect.centerx:
                direction = 1
            else:
                direction = -1
            self.knockback_distance = direction * 12

        


    #handle animation update
    def update(self, target):
        #check what action player performed
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.update_action(10)
        elif target.health <= 0:
            self.victory = True
            self.update_action(9)

        elif self.hit == True:
            self.update_action(8)#hit/hurt
        elif self.attacking == True:
            if self.attack_type == 1:
                self.update_action(3) #s.L
            elif self.attack_type == 2:
                self.update_action(4) 
            elif self.attack_type == 3:
                self.update_action(6)#c.L  
            elif self.attack_type == 4:
                self.update_action(7)#c.h        
        elif self.walking == True:
            if self.crouching == True:
                self.update_action(5)#crouch
            else:
                self.update_action(1) #walk
        elif self.walking_back == True:
            if self.crouching == True:
                self.update_action(5)#crouch
            else:
                self.update_action(2) #walk back
        elif self.crouching == True:
            self.update_action(5)#crouch
        else:
            self.update_action(0) #idle
   
        #amount of time to get to the next frame
        animation_cooldown = 30
        self.image = self.animation_list[self.action][self.frame_index]
        
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        #check if animation has finished
        if self.frame_index >= len(self.animation_list[self.action]):
            #check if player is defeated then end the animation
            if self.alive == False:
                self.frame_index = len(self.animation_list[self.action]) - 1
            elif self.victory == True:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0
                #check if an attact was executed
                if self.action == 3 or self.action == 4 or self.action == 6 or self.action == 7:
                    self.attacking = False
                    self.attack_cooldown = 5 #adjust for frame data
                #check if damage was taken
                if self.action == 8:
                    self.hit = False
                    #if the player was in the middle of an attack, then attack is stopped
                    self.attacking = False
                    self.attack_cooldown = 10 #need to adjust for frame data

    def s_L_attack(self, surface, target):
        if self.attack_cooldown == 0:
            self.attacking = True
            attacking_rect = pygame.Rect(self.rect.centerx - (2 * self.rect.width * self.flip), self.rect.y, 1.7 * self.rect.width, self.rect.height)  
            #if attack is blocked
            if attacking_rect.colliderect(target.rect) and target.block == True:
                pass
            elif attacking_rect.colliderect(target.rect):
                target.health -= 10
                target.hit = True
                target.apply_knockback(self, 1)
                
            pygame.draw.rect(surface, (0, 255, 0), attacking_rect)
            
    
    def s_H_attack(self, surface, target):
        if self.attack_cooldown == 0:
            self.attacking = True
            attacking_rect = pygame.Rect(self.rect.centerx - (2 * self.rect.width * self.flip), self.rect.y, 2.5 * self.rect.width, self.rect.height)
            if attacking_rect.colliderect(target.rect) and target.block == True and target.crouching == False:
                pass
            elif attacking_rect.colliderect(target.rect):
                target.health -= 20
                target.hit = True
                target.apply_knockback(self, 2)
            pygame.draw.rect(surface, (0, 255, 0), attacking_rect)

    def c_L_attack(self, surface, target):
        if self.attack_cooldown == 0:
            self.attacking = True
            attacking_rect = pygame.Rect(self.rect.centerx - (2 * self.rect.width * self.flip), self.rect.y, 1.7 * self.rect.width, self.rect.height)  
            if attacking_rect.colliderect(target.rect) and target.block == True and target.crouching == True:
                pass
            elif attacking_rect.colliderect(target.rect):
                target.health -= 10
                target.hit = True
                target.apply_knockback(self, 3)
            pygame.draw.rect(surface, (0, 255, 0), attacking_rect)     

    def c_H_attack(self, surface, target):
        if self.attack_cooldown == 0:
            self.attacking = True
            attacking_rect = pygame.Rect(self.rect.centerx - (2 * self.rect.width * self.flip), self.rect.y, 2.3 * self.rect.width, self.rect.height/2) 
            if attacking_rect.colliderect(target.rect) and target.block == True and target.crouching == True:
                pass
            elif attacking_rect.colliderect(target.rect):
                target.health -= 10
                target.hit = True
                target.apply_knockback(self, 4)
            pygame.draw.rect(surface, (0, 255, 0), attacking_rect)   

        
    def update_action(self, new_action):
        #check if new action is different to the prev one
        if new_action != self.action:
            self.action = new_action
            #update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        pygame.draw.rect(surface, (255, 0, 0), self.rect)
        surface.blit(img, (self.rect.x - (self.offset[0] * self.image_scale), self.rect.y - (self.offset[1] * self.image_scale)))
