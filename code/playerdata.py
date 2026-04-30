##########player data###########
import pygame
from settings import *
player_img = pygame.image.load(os.path.join(image_path, "player.png")).convert_alpha()


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites):
        super().__init__(groups)
        ## player sprite ##
        self.image = pygame.transform.scale(player_img, (64, 64))
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(0, -24)
        self.spawn_pos = pos
        self.y_sort = True
        
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
            "attack": 20,
            "defence": 0,
            "spell" : 0,
            "healing": 2,
            "health": 20
            }
        
        self.current_health = 20
        
        self.walkspeed = 5
        self.sprintspeed = 10
        
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
