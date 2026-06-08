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
LEVELS = ["../map/forest map 1.tmx",
          "../map/forest map 2.tmx",
          "../map/castle map 1.tmx",
          "../map/castle map 2.tmx"
          ]


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
        
        self.current_level = 0
        self.level = Level(LEVELS[self.current_level])
        
    def next_level(self):
        self.current_level += 1
        
        if self.current_level >= len(LEVELS):
            self.current_level = 0
            
        self.level.load_level(LEVELS[self.current_level])
        
    def run(self):
        while True:
    
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_n:
                        self.next_level()
        
                self.level.handle_input(event)
                
            #self.screen.fill('black')
            self.level.run()
            
            if self.level.finished_level:
                self.next_level()
            
            fps = self.clock.get_fps()
            fps_text = self.font.render(f'FPS: {int(fps)}', True, (255, 255, 255))
            self.screen.blit(fps_text, (10, 10))
            
            pygame.display.update()
            self.clock.tick(FPS)
            
if __name__ == '__main__':
    game = Game()
    game.run()

############ licences #############
# Copyright 2021 The Pixelify Sans Project Authors (https://github.com/eifetx/Pixelify-Sans)a