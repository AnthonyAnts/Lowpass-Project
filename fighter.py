import pygame

class Fighter():
    def __init__(self, player, x, y, flip, data, sprite_sheet, animation_steps, vfx_sheet, vfx_animation_steps, controls, sounds):
        self.player = player
        self.size = data[0]
        self.image_scale = data[1]
        self.offset = data[2]
        self.flip = flip
        self.controls = controls
        self.sounds = sounds

        # animations
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

        # states
        self.action = "idle"
        self.frame_index = 0
        self.image = self.animations[self.action][self.frame_index]
        self.rect = pygame.Rect(x, y, 155, 260) # hurtbox
        self.walking = False
        self.walking_back = False
        self.block_type = None #blocking high or low
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
        self.sound_played = False

        # attacks
        self.hitstop = 0
        self.stun_timer = 0
        self.knockback_dx = 0
        self.knockback_cooldown = 0
        self.attack_data = {}
        self.attack_timer = 0
        self.attack_state = None
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

    def move(self, screen_width, target, round_over, vfx_group):
        SPEED = 15
        dx = 0

        self.walking = False
        self.walking_back = False
        self.crouching = False
        self.block = False

        key = pygame.key.get_pressed()

        # face opponent
        self.flip = target.rect.centerx < self.rect.centerx

        # knockback
        if self.knockback_cooldown > 0:
            self.knockback_cooldown -= 1
            self.rect.x += self.knockback_dx

        # stun
        if self.stun_timer > 0:
            self.stun_timer -= 1
        
        c_left = key[self.controls['left']]
        c_right = key[self.controls['right']]
        c_down = key[self.controls['down']]

        btn_light = key[self.controls['light']] and not self.prev_key[self.controls['light']]
        btn_heavy = key[self.controls['heavy']] and not self.prev_key[self.controls['heavy']]

        can_act = self.stun_timer == 0 and not self.attacking and self.alive and not round_over and self.hurt_timer == 0
        
        # movement and attacks
        if can_act:
            self.block = (self.flip and c_right) or (not self.flip and c_left)

            if c_down: self.crouching = True
            elif c_left: 
                self.walking_back = not self.flip
                self.walking = self.flip
                dx = (-SPEED + 10) if self.walking_back else -SPEED
            elif c_right: 
                self.walking_back = self.flip
                self.walking = not self.flip 
                dx = (SPEED - 10) if self.walking_back else SPEED
        
    
            if btn_light and self.crouching:
                self.start_attack("crouching_light")
            elif btn_heavy and self.crouching: 
                self.start_attack("crouching_heavy")
            elif btn_light:
                self.start_attack("standing_light")
            elif btn_heavy:
                self.start_attack("standing_heavy")

        # screen bounds
        if self.rect.left + dx < 0: dx = -self.rect.left
        if self.rect.right + dx > screen_width: dx = screen_width - self.rect.right

        # collision, makes sure no overlap
        if self.rect.move(dx, 0).colliderect(target.rect): dx = 0

        if self.attack_cooldown > 0: self.attack_cooldown -= 1

        self.attack(target, vfx_group)
        self.rect.x += dx
        self.prev_key = key

    def apply_knockback(self, amount, flip):
        direction = -1 if flip else 1
        self.knockback_dx = direction * (amount / 5)
        self.knockback_cooldown = 5

    def stun_on_hit(self, duration): self.stun_timer = duration
    def stun_on_block(self, duration): self.stun_timer = duration
    def on_target_block(self, duration): self.stun_timer = duration

    def update(self, target):
        if self.health <= 0:
            self.alive = False

        # defeat state overrides everything
        if not self.alive:
            if self.action != "defeat":
                self.update_action("defeat") # once dead, frame_index = 0
                self.stun_timer = 5 # very lazy way to stop player from pressing any buttons once defeated
                if not self.sound_played:
                    self.sounds["hurt"].play()
                    self.sounds["victory"].play()
            
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

        # attacking
        if self.attacking:
            self.update_action(self.attack_type)
            if not self.sound_played:
                if self.attack_type == "standing_light":
                    self.sounds["standing_light"].play()

                elif self.attack_type == "standing_heavy":
                    self.sounds["standing_heavy"].play()
                    
                elif self.attack_type == "crouching_light":
                    self.sounds["crouching_light"].play()
                    
                elif self.attack_type == "crouching_heavy":
                    self.sounds["crouching_heavy"].play()
                    
                self.sound_played = True
        # hitstop
        elif self.hitstop > 0:
            self.hitstop -= 1
            return
        
        # hurt flag
        elif self.hurt_timer > 0:
            self.hurt_timer -= 1
            self.hit = True
            self.update_action("hurt")
            if not self.sound_played:
                if target.attack_type == "standing_light" or target.attack_type == "crouching_light":
                    self.sounds["light_hit_sfx"].play()
                    self.sounds["hurt"].play()

                elif target.attack_type == "standing_heavy" or target.attack_type == "crouching_heavy":
                    self.sounds["heavy_hit_sfx"].play()
                    self.sounds["hurt"].play()

                self.sound_played = True

        # blocking
        elif self.block and (self.walking_back or self.crouching): 
            self.update_action("crouch" if self.crouching else "walk_back")

        # idle
        else:
            if target.health <= 0:
                self.victory = True
                self.update_action("victory")

            elif self.walking:
                self.update_action("walk")

            elif self.walking_back:
                self.update_action("walk_back")

            elif self.crouching:
                self.update_action("crouch")

            else:
                self.update_action("idle")

        # for attack animations getting attack frames for
        # frame indexing and hitbox timing
        if self.attacking:
            total_frames = len(self.animations[self.action])
            total_attack_frames = (self.attack_data["startup"] + self.attack_data["active"] + self.attack_data["recovery"])
            # Out of Index Error Handling
            progress = min(self.attack_timer / max(1, total_attack_frames), 1) # to make sure it doesn't crash - some values may be out of index, therefore we squash them into a range of 0-1
            self.frame_index = int(progress * (total_frames - 1))

        else:
            # normal animations (idle, walk, etc.)
            self.anim_counter += 1
            if self.anim_counter >= self.animation_data[self.action].get("speed", 4):
                self.frame_index += 1
                self.anim_counter = 0

            if self.frame_index >= len(self.animations[self.action]):
                self.frame_index = len(self.animations[self.action]) - 1 if self.action == "victory" else 0
        
        # Out of Index Error Handling
        self.frame_index = max(0, min(self.frame_index, len(self.animations[self.action]) - 1))
        # reset animation
        self.image = self.animations[self.action][self.frame_index]
        # i love procedural programming

        # debug
        # if self.player == 2:
            # print(f"Victory: {self.victory} | State: {self.alive} | Action: {self.action} | Blocking: {self.block} | WalkBack: {self.walking_back}")
            # print(f"Stun: {self.stun_timer} | Target Stun: {target.stun_timer}")
        
    def attack(self, target, vfx_group):
        if not self.attacking: return

        self.attack_timer += 1
        startup = self.attack_data["startup"]
        active = self.attack_data["active"]
        recovery = self.attack_data["recovery"]
        hitbox = self.attack_data.get("hitbox")
        total_duration = startup + active + recovery

        if startup < self.attack_timer <= startup + active:
            if not hitbox or self.attack_landed: return

            width = self.rect.width * hitbox["width_multiplier"]
            height = self.rect.height * hitbox["height_multiplier"]
            x = self.rect.centerx - self.rect.width * 0.5 - width if self.flip else self.rect.centerx + self.rect.width * 0.5
            y = self.rect.y
            attacking_rect = pygame.Rect(x, y, width, height)

            # debug spawning hitbox
            # pygame.draw.rect(surface, (0, 255, 0), attacking_rect)

            if attacking_rect.colliderect(target.rect):
                self.hitstop = 2 # hitstop is for animations to make them look cooler
                target.hitstop = 4
                
                is_low = "crouching" in self.attack_type
                is_overhead = self.attack_type == "standing_heavy"
                can_block = False

                if target.block:
                    if self.attack_type == "standing_heavy":
                        can_block = not target.crouching

                    elif self.attack_type == "standing_light":
                        can_block = True

                    elif self.attack_type in ["crouching_light", "crouching_heavy"]:
                        can_block = target.crouching
                
                if can_block:
                    self.attack_landed = True
                    block_data = self.attack_data["on_block"]
                    t_block_data = self.attack_data["on_target_block"]

                    target.apply_knockback(block_data["knockback"], self.flip)
                    target.stun_on_block(block_data["stun"])
                    self.on_target_block(t_block_data["stun"])
                    self.apply_knockback(t_block_data["knockback"], not self.flip)

                    self.sounds["block"].play()
                    self.sound_played = True

                    # spawn block VFX
                    v_cfg = self.vfx_config.get("block", {})
                    x_off = v_cfg.get("x_offset", 0) * self.image_scale
                    y_off = v_cfg.get("y_offset", 0) * self.image_scale
                    vfx_x = target.rect.left + x_off if not self.flip else target.rect.right - x_off
                    vfx_group.add(VFX(vfx_x, target.rect.centery - y_off, self.vfx_animations["block"], speed=4, flip=not self.flip))
                else:
                    self.attack_landed = True
                    hit_data = self.attack_data["on_hit"]
                    target.hurt_timer = hit_data["stun"]
                    target.health -= hit_data["damage"]
                    target.apply_knockback(hit_data["knockback"], self.flip)
                    target.stun_on_hit(hit_data["stun"])

            # attack reset  
        if self.attack_timer >= total_duration:
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
            self.sound_played = False

    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        draw_x = self.rect.x - (self.offset[0] * self.image_scale)
        draw_y = self.rect.y - (self.offset[1] * self.image_scale)
        surface.blit(img, (draw_x, draw_y))

        # vfx handling
        if self.attacking:
            # diabolical vfx_anim fetch without needing funky coding
            vfx_name = f"{self.attack_type}_vfx"
            if vfx_name in self.vfx_animations:
                vfx_list = self.vfx_animations[vfx_name]
                # Out of Index Error Handling
                vfx_frame_idx = min(self.frame_index, len(vfx_list) - 1)
                vfx_img = pygame.transform.flip(vfx_list[vfx_frame_idx], self.flip, False)
                x_offset = self.vfx_config[vfx_name].get("x_offset", 0)
                y_offset = self.vfx_config[vfx_name].get("y_offset", 0)

                if self.flip: x_offset = -x_offset

                surface.blit(vfx_img, (draw_x + (x_offset * self.image_scale), draw_y + (y_offset * self.image_scale)))

class VFX(pygame.sprite.Sprite):
    def __init__(self, x, y, anim_list, speed=4, flip=False):
        super().__init__()
        self.frames = anim_list
        self.flip = flip
        self.frame_index = 0
        self.speed = speed
        self.counter = 0
        
        self.image = pygame.transform.flip(self.frames[self.frame_index], self.flip, False)
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
                self.image = pygame.transform.flip(self.frames[self.frame_index], self.flip, False)
