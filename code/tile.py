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