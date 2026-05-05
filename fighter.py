import pygame

class Fighter():
    def __init__(self, player, x, y, flip, data, sprite_sheet, animation_steps, vfx_sheet, vfx_animation_steps):
        self.player = player
        self.size = data[0]
        self.image_scale = data[1]
        self.offset = data[2]
        self.flip = flip
        self.animation_data = animation_steps
        self.animations = self.load_images(sprite_sheet, animation_steps)
        self.vfx_animations = self.load_vfx(vfx_sheet, vfx_animation_steps)
        self.vfx_config = vfx_animation_steps

        # attack data
        self.attack_profiles = {
            "standing_light": animation_steps["standing_light"],
            "standing_heavy": animation_steps["standing_heavy"],
            "crouching_light": animation_steps["crouching_light"],
            "crouching_heavy": animation_steps["crouching_heavy"],
        }

        self.action = "idle"
        self.frame_index = 0
        self.image = self.animations[self.action][self.frame_index]

        self.rect = pygame.Rect((x, y, 155, 260))

        # states
        self.walking = False
        self.walking_back = False
        self.crouching = False
        self.attacking = False
        self.attack_type = None
        self.attack_cooldown = 0
        self.hurt_timer = 0
        self.hit = False
        self.health = 100
        self.alive = True
        self.block = False
        self.victory = False

        # hitstop
        self.hitstop = 0

        # knockback
        self.knockback_dx = 0
        self.knockback_cooldown = 0

        # stun
        self.stun_timer = 0

        # attack system
        self.attack_timer = 0
        self.attack_state = None
        self.attack_data = {}
        self.attack_landed = False

        # animation timing
        self.anim_counter = 0

        self.prev_key = pygame.key.get_pressed()

    def load_vfx(self, vfx_sheet, vfx_animation_steps):
        vfx_animations = {}
        for y, (name, data) in enumerate(vfx_animation_steps.items()):
            frames = data["frames"]
            alpha_value = data.get("alpha", 255)
            frame_list = []

            for x in range(frames):
                img = vfx_sheet.subsurface(
                    x * self.size, 
                    y * self.size, 
                    self.size, 
                    self.size
                )
                img = pygame.transform.scale(
                    img, 
                    (self.size * self.image_scale, self.size * self.image_scale)
                )

                img.set_alpha(alpha_value)

                frame_list.append(img)

            vfx_animations[name] = frame_list
        return vfx_animations

    def load_images(self, sprite_sheet, animation_steps):
        animations = {}
        for y, (name, data) in enumerate(animation_steps.items()):
            frames = data["frames"]
            frame_list = []

            for x in range(frames):
                img = sprite_sheet.subsurface(
                    x * self.size,
                    y * self.size,
                    self.size,
                    self.size
                )
                img = pygame.transform.scale(
                    img,
                    (self.size * self.image_scale, self.size * self.image_scale)
                )
                frame_list.append(img)

            animations[name] = frame_list

        return animations

    def move(self, screen_width, surface, target, round_over, vfx_group):
        SPEED = 15
        dx = 0

        self.walking = False
        self.walking_back = False
        self.crouching = False
        self.block = False

        key = pygame.key.get_pressed()

        # face opponent
        self.flip = target.rect.centerx < self.rect.centerx

        # block
        if not self.attacking:
            if self.player == 1:
                self.block = (self.flip and key[pygame.K_d]) or (not self.flip and key[pygame.K_a])
            else:
                self.block = (self.flip and key[pygame.K_RIGHT]) or (not self.flip and key[pygame.K_LEFT])
        else:
            self.block = False

        # knockback
        if self.knockback_cooldown > 0:
            self.knockback_cooldown -= 1
            self.rect.x += self.knockback_dx

        # stun
        if self.stun_timer > 0:
            self.stun_timer -= 1

        if self.stun_timer == 0 and not self.attacking and self.alive and not round_over and self.hurt_timer == 0:
            if self.player == 1:
                if key[pygame.K_a]:
                    dx = -SPEED + 10 # walking back speed should be slower
                    self.walking_back = True
                if key[pygame.K_d]:
                    dx = SPEED
                    self.walking = True
                if key[pygame.K_s]:
                    dx = 0
                    self.crouching = True
            
            else: # player 2 move input
                if key[pygame.K_LEFT]:
                    dx = -SPEED
                    self.walking = True
                if key[pygame.K_RIGHT]:
                    dx = SPEED - 10 # walking back speed should be slower
                    self.walking_back = True
                if key[pygame.K_DOWN]:
                    dx = 0
                    self.crouching = True
 
        # attack inputs
        if self.stun_timer == 0 and not self.attacking and self.alive and not round_over and self.hurt_timer == 0:
            if self.player == 1:
                is_crouching = key[pygame.K_s]
                j = key[pygame.K_j] and not self.prev_key[pygame.K_j]
                k = key[pygame.K_k] and not self.prev_key[pygame.K_k]

                if j and is_crouching:
                    self.start_attack("crouching_light")
                elif k and is_crouching:
                    self.start_attack("crouching_heavy")
                elif j:
                    self.start_attack("standing_light")
                elif k:
                    self.start_attack("standing_heavy")

            else: #player 2 attack input
                is_crouching = key[pygame.K_DOWN]
                j = key[pygame.K_KP_2] and not self.prev_key[pygame.K_KP_2]
                k = key[pygame.K_KP_3] and not self.prev_key[pygame.K_KP_3]

                if j and is_crouching:
                    self.start_attack("crouching_light")
                elif k and is_crouching:
                    self.start_attack("crouching_heavy")
                elif j:
                    self.start_attack("standing_light")
                elif k:
                    self.start_attack("standing_heavy")

        # screen bounds
        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > screen_width:
            dx = screen_width - self.rect.right

        # collision
        if self.rect.move(dx, 0).colliderect(target.rect):
            dx = 0

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        self.attack(target, surface, vfx_group)

        self.rect.x += dx
        self.prev_key = key

    def apply_knockback(self, amount, flip):
        direction = -1 if flip else 1
        self.knockback_dx = direction * (amount / 5)
        self.knockback_cooldown = 5

    def stun_on_hit(self, duration):
        self.stun_timer = duration

    def stun_on_block(self, duration):
        self.stun_timer = duration

    def on_target_block(self, duration):
        self.stun_timer = duration

    def update(self, target):
        # time check: 2:12 am
        # i really love procedural programming

        # defeat handling
        # this is first so it overrides all functions when defeat is done
        # this is to ensure inputs can't be overridden and to maintain
        # consistency for animation drawing
        if not self.alive:
            if self.action != "defeat":
                self.update_action("defeat") # once dead, frame_index = 0
                self.stun_timer = 5 # very lazy way to stop player from pressing any buttons once defeated
            
            anim = self.animations["defeat"]
            self.anim_counter += 1
            speed = self.animation_data["defeat"].get("speed", 4)

            # ensure defeat animation plays consistently
            if self.anim_counter >= speed:
                if self.frame_index < len(anim) - 1:
                    self.frame_index += 1
                self.anim_counter = 0
            
            self.frame_index = max(0, min(self.frame_index, len(anim) - 1)) # asymptotic
            self.image = anim[min(self.frame_index, len(anim) - 1)]
            return

        # i hate doing this but i'm gonna comment and leave a section
        # for every if/elif here

        # attacking
        if self.attacking:
            self.update_action(self.attack_type)
        
        # # hitstop
        elif self.hitstop > 0:
            self.hitstop -= 1
            return
        
        # hurt flag
        elif self.hurt_timer > 0:
            self.hurt_timer -= 1
            self.hit = True
            self.update_action("hurt")

        # blocking
        elif self.block: 
            if self.walking_back and not self.crouching:
                self.update_action("walk_back") # temporarily using walk_back until proper block sprite is added
            elif self.crouching:
                self.update_action("crouch")
        
        # idle
        else:
            if self.health <= 0:
                self.alive = False
            elif target.health <= 0:
                self.victory = True
                self.update_action("victory")
            elif self.hurt_timer > 0:
                self.update_action("hurt")
            elif self.alive: # just in case:
                if self.walking:
                    self.update_action("walk")
                elif self.walking_back:
                    self.update_action("walk_back")
                    # self.block
                elif self.crouching:
                    self.update_action("crouch")
                    # self.block
                else:
                    self.update_action("idle")

        # for attack animations getting attack frames for
        # frame indexing and hitbox timing
        if self.attacking:
            total_frames = len(self.animations[self.action])
            total_attack_frames = (
                self.attack_data["startup"] +
                self.attack_data["active"] +
                self.attack_data["recovery"]
            )
            # Out of Index Error Handling
            progress = min(self.attack_timer / max(1, total_attack_frames), 1) # to make sure it doesn't crash - some values may be out of index, therefore we squash them into a range of 0-1
            self.frame_index = int(progress * (total_frames - 1))

        else:
            # normal animations (idle, walk, etc.)
            anim_speed = self.animation_data[self.action].get("speed", 4)
            self.anim_counter += 1
            if self.anim_counter >= anim_speed:
                self.frame_index += 1
                self.anim_counter = 0

            if self.frame_index >= len(self.animations[self.action]):
                if self.action == "victory":
                    self.frame_index = len(self.animations[self.action]) - 1
                else:
                    self.frame_index = 0
        
        current_anim_list = self.animations[self.action]
        # Out of Index Error Handling
        self.frame_index = max(0, min(self.frame_index, len(current_anim_list) - 1))
        # reset animation
        self.image = self.animations[self.action][self.frame_index]
        # i love procedural programming

        # debug
        if self.player == 2:
            print(f"Action: {self.action} | Blocking: {self.block} | WalkBack: {self.walking_back}")
            # print(f"Stun: {self.stun_timer} | Target Stun: {target.stun_timer}")
        
    def attack(self, target, surface, vfx_group):
        if not self.attacking:
            return

        self.attack_timer += 1

        startup = self.attack_data["startup"]
        active = self.attack_data["active"]
        recovery = self.attack_data["recovery"]
        hitbox = self.attack_data.get("hitbox")

        if self.attack_timer <= startup:
            return

        elif self.attack_timer <= startup + active:
            if not hitbox or self.attack_landed:
                return

            width = self.rect.width * hitbox["width_multiplier"]
            height = self.rect.height * hitbox["height_multiplier"]

            if self.flip:
                x = self.rect.centerx - self.rect.width * 0.5 - width
            else:
                x = self.rect.centerx + self.rect.width * 0.5

            y = self.rect.y
            attacking_rect = pygame.Rect(x, y, width, height)

            # debug spawning hitbox
            pygame.draw.rect(surface, (0, 255, 0), attacking_rect)

            if attacking_rect.colliderect(target.rect):
                self.hitstop = 2 # hitstop is for animations to make them look cooler
                target.hitstop = 4

                if target.crouching and (self.attack_type == "crouching_light" or self.attack_type == "crouching_heavy") and not target.block: # crouching block beats all crouching moves
                    self.attack_landed = True # flag to set gatling on hit confirm
                    hit = self.attack_data["on_hit"]
                    target.hit = True
                    target.hurt_timer = hit["stun"]
                    target.health -= hit["damage"]
                    target.apply_knockback(hit["knockback"], self.flip)
                    target.stun_on_hit(hit["stun"])

                elif (target.crouching or target.block) and self.attack_type == "standing_heavy": # standing_heavy beats crouching block
                    self.attack_landed = True # flag to set gatling on hit confirm
                    hit = self.attack_data["on_hit"]
                    target.hit = True
                    target.hurt_timer = hit["stun"]
                    target.health -= hit["damage"]
                    target.apply_knockback(hit["knockback"], self.flip)
                    target.stun_on_hit(hit["stun"])

                elif target.block and target.crouching and not target.block:
                    self.attack_landed = False # flag to set no gatling on block
                    block = self.attack_data["on_block"]
                    target_block = self.attack_data["on_target_block"]
                    target.hit = False

                    # apply target stun and knockback
                    target.apply_knockback(block["knockback"], self.flip)
                    target.stun_on_block(block["stun"])

                    # apply self stun and knockback
                    self.on_target_block(target_block["stun"])
                    if self.flip:
                        self.apply_knockback(target_block["knockback"], False)
                    else:
                        self.apply_knockback(target_block["knockback"], True)
                    

                    # player 1 block vfx
                    x_offset = self.vfx_config["block"].get("x_offset", 0) * self.image_scale
                    y_offset = self.vfx_config["block"].get("y_offset", 0) * self.image_scale

                    if not self.flip:
                        block_vfx_x = target.rect.left + x_offset
                        block_vfx_flip = True
                    else: # player 2
                        block_vfx_x = target.rect.right - x_offset
                        block_vfx_flip = False

                    block_vfx_y = target.rect.centery - y_offset
                    block_vfx = VFX(block_vfx_x, block_vfx_y, self.vfx_animations["block"], speed = 4, flip = block_vfx_flip)
                    vfx_group.add(block_vfx)
                
                else:
                    self.attack_landed = False # flag to set no gatling on block
                    block = self.attack_data["on_block"]
                    target_block = self.attack_data["on_target_block"]
                    target.hit = False

                    # apply target stun and knockback
                    target.apply_knockback(block["knockback"], self.flip)
                    target.stun_on_block(block["stun"])

                    # apply self stun and knockback
                    self.on_target_block(target_block["stun"])
                    if self.flip:
                        self.apply_knockback(target_block["knockback"], False)
                    else:
                        self.apply_knockback(target_block["knockback"], True)
                    

                    # player 1 block vfx
                    x_offset = self.vfx_config["block"].get("x_offset", 0) * self.image_scale
                    y_offset = self.vfx_config["block"].get("y_offset", 0) * self.image_scale

                    if not self.flip:
                        block_vfx_x = target.rect.left + x_offset
                        block_vfx_flip = True
                    else: # player 2
                        block_vfx_x = target.rect.right - x_offset
                        block_vfx_flip = False

                    block_vfx_y = target.rect.centery - y_offset
                    block_vfx = VFX(block_vfx_x, block_vfx_y, self.vfx_animations["block"], speed = 4, flip = block_vfx_flip)
                    vfx_group.add(block_vfx)
        # attack reset
        elif self.attack_timer > startup + active + recovery:
            self.attacking = False
            self.attack_timer = 0
            self.attack_landed = False
            self.attack_cooldown = recovery

    def start_attack(self, attack_type):
        if self.attacking:
            gatling = self.attack_data.get("gatling", [])

            if self.attack_landed and attack_type in gatling: #hit confirm
                self.attack_values(attack_type)
            return

        if self.attack_cooldown <= 0:
            self.attack_values(attack_type)

    def attack_values(self, attack_type): # helper function for attack logic
        self.attacking = True
        self.attack_type = attack_type
        self.attack_timer = 0
        self.frame_index = 0
        self.anim_counter = 0
        self.attack_data = self.attack_profiles[attack_type]
        self.attack_landed = False
        self.update_action(attack_type)

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.anim_counter = 0

    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        # debug
        # pygame.draw.rect(surface, (255, 0, 0), self.rect)
        # draw sora
        surface.blit(
            img,
            (
                self.rect.x - (self.offset[0] * self.image_scale),
                self.rect.y - (self.offset[1] * self.image_scale)
            )
        )

        # vfx handling
        if self.attacking:
            # diabolical vfx_anim fetch without needing funky coding
            vfx_name = f"{self.attack_type}_vfx"

            if vfx_name in self.vfx_animations:
                vfx_list = self.vfx_animations[vfx_name]
                # Out of Index Error Handling
                vfx_frame_idx = min(self.frame_index, len(vfx_list) - 1)
                vfx_img = vfx_list[vfx_frame_idx]
                # flip for p2
                vfx_img = pygame.transform.flip(vfx_img, self.flip, False)
                x_offset = self.vfx_config[vfx_name].get("x_offset", 0)
                y_offset = self.vfx_config[vfx_name].get("y_offset", 0)

                if self.flip:
                    x_offset = -x_offset
                
                draw_x = self.rect.x - (self.offset[0] * self.image_scale) + (x_offset * self.image_scale)
                draw_y = self.rect.y - (self.offset[1] * self.image_scale) + (y_offset * self.image_scale)

                surface.blit(vfx_img, (draw_x, draw_y))

class VFX(pygame.sprite.Sprite):
    def __init__(self, x, y, anim_list, speed=4, flip=False):
        super().__init__()
        self.frames = anim_list
        self.flip = flip
        self.frame_index = 0
        self.speed = speed
        self.counter = 0
        

        img = self.frames[self.frame_index]
        self.image = pygame.transform.flip(img, self.flip, False)
        self.rect = self.image.get_rect(center=(x,y))


    def update(self):
        # update animation
        self.counter += 1
        if self.counter >= self.speed:
            self.counter = 0
            self.frame_index += 1
            
            # if the animation finishes, kill the sprite
            if self.frame_index >= len(self.frames):
                self.kill() 
            else:
                img = self.frames[self.frame_index]
                self.image = pygame.transform.flip(img, self.flip, False)
