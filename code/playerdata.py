##########player data###########3
import pygame
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites):
        super().__init__(groups)
        ## player sprite ##
        self.image = pygame.Surface((64,64))
        self.image.fill((255,255,255))
        self.rect = self.image.get_rect(topleft = pos)
        self.radius = 30
        
        ## movement ##
        self.direction = pygame.math.Vector2()
        self.movespeed = 0
        
        self.obstacle_sprites = obstacle_sprites
        ## equipment ##
        self.weapon = None
        self.spell = None
        self.accessories = [None, None, None]
        ## Stats ##
        self.base_attack = 3
        self.base_defense = 0
        self.base_spell = 0
        self.base_healing = 2
        
        self.max_health = 20
        self.current_health = 20
        
        self.walkspeed = 5
        self.sprintspeed = 10
        
    def inputs(self):
        keys = pygame.key.get_pressed()
        
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
        return(self.movespeed)
            
            
    def move(self, movespeed):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()
            
        self.rect.x += self.direction.x * self.movespeed
        self.collision('horizontal')
        self.rect.y += self.direction.y * self.movespeed
        self.collision('vertical')
        
    def collision(self, direction):
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.rect.colliderect(self.rect):
                    if self.direction.x > 0:
                        self.rect.right = sprite.rect.left
                    if self.direction.x < 0:
                        self.rect.left = sprite.rect.right
                            
        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.rect.colliderect(self.rect):
                    if self.direction.y > 0:
                        self.rect.bottom = sprite.rect.top
                    if self.direction.y < 0:
                        self.rect.top = sprite.rect.bottom
                        
    def equip_accessory_to_slot(self, item, slot_index, inventory):
        old = self.accessories[slot_index]
        self.accessories[slot_index] = item
        
        item.quantity -= 1
        if item.quantity <=0:
            inventory.remove_item(item)
        
        if old:
            inventory.add_item(old)
                            
    def update(self):
        self.inputs()
        self.move(self.movespeed)
        
    @property
    def attack(self):
        total = self.base_attack
        if self.weapon:
            total += self.weapon.stat_bonus.get("attack", 0)
        for acc in self.accessories:
            if acc:
                total += acc.stat_bonus.get("attack", 0)
        return total

    @property
    def defense(self):
        total = self.base_defense
        for acc in self.accessories:
            if acc:
                total += acc.stat_bonus.get("defence", 0)
        return total
    
    @property
    def spell_dmg(self):
        total = self.base_spell
        if self.spell:
            total += self.spell.stat_bonus.get("spell", 0)
        for acc in self.accessories:
            if acc:
                total += acc.stat_bonus.get("spell", 0)
        return total
    
    @property
    def healing(self):
        total = self.base_healing
        if self.spell:
            total += self.spell.stat_bonus.get("healing", 0)
        for acc in self.accessories:
            if acc:
                total += acc.stat_bonus.get("healing", 0)
        return total
    
    @property
    def health(self):
        total = self.base_health
        for acc in self.accessories:
            if acc:
                total += acc.stat_bonus.get("health", 0)
        return total
