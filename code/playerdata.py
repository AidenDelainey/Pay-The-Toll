##########player data###########
import pygame
from settings import *
player_img = pygame.image.load(os.path.join(image_path, "player.png")).convert_alpha()


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites):
        super().__init__(groups)
        ## player sprite ##
        self.base_image = pygame.transform.scale(player_img, (64, 64))
        self.image = self.base_image
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(-15, -32)
        self.spawn_pos = pos
        self.y_sort = True
        self.facing_right = True
        
        ## movement ##
        self.direction = pygame.math.Vector2()
        self.movespeed = 0
        
        self.obstacle_sprites = obstacle_sprites
        ## equipment ##
        self.weapon = None
        self.spell = None
        self.accessories = [None, None, None]
        ## Stats ##
        self.base_stats = {
            "attack": 3,
            "defence": 0,
            "spell" : 0,
            "healing": 2,
            "health": 20
            }
        
        self.current_health = 20
        
        self.walkspeed = 20
        self.sprintspeed = 10
        self.frames = self.load_frames(player_img, 16,16)
        self.frame_index = 0
        self.animation_speed = 0.20
        
        self.image = self.frames[self.frame_index]
        self.base_image = self.image
        
        
    def load_frames(self, sheet, frame_width, frame_height):
        frames = []
        sheet_width = sheet.get_width()
        
        for x in range(0, sheet_width, frame_width):
            frame = sheet.subsurface((x, 0, frame_width, frame_height))
            frame = pygame.transform.scale(frame, (64,64))
            frames.append(frame)
        return frames
    
    def animate(self):
        if self.direction.length_squared() > 0:
            self.frame_index += self.animation_speed
            
            if self.frame_index >= len(self.frames):
                self.frame_index = 0
            self.base_image = self.frames[int(self.frame_index)]
        else:
            self.frame_index = 0
            self.base_image = self.frames[0]
    
    def inputs(self):
        keys = pygame.key.get_pressed()
        
        # movement
        if keys[pygame.K_LSHIFT]:
            self.movespeed = self.sprintspeed
        else:
            self.movespeed = self.walkspeed
        
        if keys[pygame.K_w]:
            self.direction.y = -1
        elif keys[pygame.K_s]:
            self.direction.y = 1
        else:
            self.direction.y = 0
            
        if keys[pygame.K_d]:
            self.direction.x = 1
        elif keys[pygame.K_a]:
            self.direction.x = -1
        else:
            self.direction.x = 0            
            
    def move(self):
        if self.direction.length_squared() > 0:
            self.direction = self.direction.normalize()
            
        self.hitbox.x += self.direction.x * self.movespeed
        self.collision('horizontal')
        self.hitbox.y += self.direction.y * self.movespeed
        self.collision('vertical')
        self.rect.center = self.hitbox.center
        
    def collision(self, direction):
        for sprite in self.obstacle_sprites:
            if sprite.hitbox.colliderect(self.hitbox):
        
                if direction == 'horizontal':
                    if self.direction.x > 0:
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:
                        self.hitbox.left = sprite.hitbox.right
                            
                if direction == 'vertical':
                    if self.direction.y > 0:
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:
                        self.hitbox.top = sprite.hitbox.bottom
                        
    def equip_accessory_to_slot(self, item, slot_index, inventory):
        old_max_hp = self.max_hp
        
        old = self.accessories[slot_index]
        self.accessories[slot_index] = item
        
        item.quantity -= 1
        if item.quantity <=0:
            inventory.remove_item(item)
        
        if old:
            inventory.add_item(old)
        
        self.rescale_health(old_max_hp)
        
        self.old_max_hp = self.max_hp
                            
    def update(self):
        self.inputs()
        self.move()
        self.animate()
        
        if self.direction.x < 0:
            self.facing_right = False
        elif self.direction.x > 0:
            self.facing_right = True

        if self.facing_right:
            self.image = self.base_image
        else:
            self.image = pygame.transform.flip(self.base_image, True, False)
          
            self.current_health = min(self.current_health, self.max_hp)
          
    def rescale_health(self, old_max_hp):
        if old_max_hp > 0:
            ratio = self.current_health / old_max_hp
            self.current_health = ratio * self.max_hp
        
    def get_stat(self, stat):
        total = self.base_stats.get(stat, 0)
        
        equipment = [self.weapon, self.spell] + self.accessories

        for item in equipment:
            if item:
                total += item.stat_bonus.get(stat, 0)

        return total

    @property
    def max_hp(self):
        return self.get_stat("health")
