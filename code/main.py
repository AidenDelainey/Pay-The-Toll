##----------------------##
#) game name            (#
#) Aiden Delainey       (#
#) feb 2/2026           (#
#) ver 0.0.1            (#
##----------------------##

################ imports ###############
import pygame, sys
from settings import *
pygame.display.set_mode((WIDTH, HEIGHT)) # <-- don't remove or move
from level import Level

icon_img = pygame.image.load(os.path.join(enemies_path, "gnome", "idle.png" )).convert_alpha()

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        pygame.font.init()
        self.font = pygame.font.Font(font_path, 20)
        
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Pay The Toll')
        pygame.display.set_icon(icon_img)
        
        self.clock = pygame.time.Clock()
        self.level = Level()
        
    def run(self):
        while True:
    
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
        
                self.level.handle_input(event)
                
            #self.screen.fill('black')
            self.level.run()
            
            fps = self.clock.get_fps()
            fps_text = self.font.render(f'FPS: {int(fps)}', True, (255, 255, 255))
            self.screen.blit(fps_text, (10, 10))
            
            pygame.display.update()
            self.clock.tick(FPS)
            
if __name__ == '__main__':
    game = Game()
    game.run()

############ licences #############
# Copyright 2021 The Pixelify Sans Project Authors (https://github.com/eifetx/Pixelify-Sans)