##### tile data ####
import pygame
from settings import *

class Tile(pygame.sprite.Sprite):
    def __init__(self,pos,surf,groups):
        super().__init__(groups)
        if surf:
            self.image = pygame.transform.scale(surf, (64,64))
        else:
            self.image = pygame.Surface((64,64))
            self.image.fill((0,0,255))
        
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(0,-15)
        self.y_sort = False
        self.always_on_top = False
        
class AnimatedTile(pygame.sprite.Sprite):
    def __init__(self, pos, frames, tmx_data, groups):
        super().__init__(groups)
        
        self.frames = []
        self.frame_duration = []
        
        for frame in frames:
            gid = frame.gid
            duration = frame.duration
            
            image = tmx_data.get_tile_image_by_gid(gid)
            image = pygame.transform.scale(image, (64, 64))
            self.frames.append(image)
            self.frame_duration.append(duration)
        
        self.frame_index = 0
        self.timer = 0
        self.last_time = pygame.time.get_ticks()
        
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=pos)
        
        self.always_on_top = True
        
    def update(self):
        now = pygame.time.get_ticks()
        dt = now - self.last_time
        self.last_time = now
        
        self.timer += dt
        
        if self.timer >= self.frame_duration[self.frame_index]:
            self.timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]
