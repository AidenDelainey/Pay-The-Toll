##----------------------##
#) game name            (#
#) Aiden Delainey       (#
#) feb 2/2026           (#
#) ver 0.0.1            (#
##----------------------##

################ imports ###############
import pygame, sys
from settings import *
from level import Level

class Game:
    def __init__(self):
        pygame.init()
        
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Game')
        
        self.clock = pygame.time.Clock()
        self.level = Level()
        
    def run(self):
        while True:
    
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
        
                self.level.handle_input(event)
                    
            self.screen.fill('black')
            self.level.run()
            
            pygame.display.update()
            self.clock.tick(FPS)
            
if __name__ == '__main__':
    game = Game()
    game.run()
############ licences #############
# Copyright 2021 The Pixelify Sans Project Authors (https://github.com/eifetx/Pixelify-Sans)