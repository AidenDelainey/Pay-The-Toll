##### basic map ######
import pygame
from settings import *
from tile import Tile
from itemdata import WorldItem, Item, ITEM_DATABASE
from playerdata import Player
from inventory import Inventory

inv_open_snd = pygame.mixer.Sound(os.path.join(sound_path, "inventory open.mp3"))
inv_close_snd = pygame.mixer.Sound(os.path.join(sound_path, "inventory close.mp3"))

ITEM_SPAWNS = {
    "i": ("000", "flimsy_dagger"),
    "s": ("001", "wooden_wand"),
    "h": ("002", "simple_bracers"),
    "d": ("003", "silver_ring")
    }

class Level:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.visable_sprites = YSortCameraGroup()
        self.item_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()
        
        self.create_map()
        
        self.inventory = Inventory(self.player)
        self.inventory_open = False
        
    def handle_input(self, event):
        if event.type == pygame.KEYUP and event.key == pygame.K_TAB:
            self.inventory_open = not self.inventory_open
            
            if not self.inventory_open:
                inv_close_snd.play()
            else:
                inv_open_snd.play()
                
            if self.inventory_open:
                self.inventory.handle_input(event)
        
    def create_map(self):
        for row_index,row in enumerate(WORLD_MAP):
            for col_index, col in enumerate(row):
                x = col_index * TILESIZE
                y = row_index * TILESIZE
                pos = (x,y)
                
                if col == 'x':
                    Tile((x,y),[self.visable_sprites,self.obstacle_sprites])
                elif col == 'p':
                    self.player = Player((x,y),[self.visable_sprites],self.obstacle_sprites)
                elif col in ITEM_SPAWNS:
                    item_name, db_key = ITEM_SPAWNS[col]
                    item = Item(item_name, ITEM_DATABASE[db_key])
                    WorldItem(pos, item, [self.visable_sprites, self.item_sprites])
                
    def run(self):
        self.visable_sprites.custom_draw(self.player)

        if not self.inventory_open:
            self.visable_sprites.update()
            
            collided_items = pygame.sprite.spritecollide(
                self.player,
                self.item_sprites,
                True
            )
            for item_sprite in collided_items:
                self.inventory.add_item(item_sprite.item_data)
            
        if self.inventory_open:
            self.inventory.draw()
        
class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self,):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_width() // 2
        self.half_height = self.display_surface.get_height() // 2
        
        
        self.camera_pos = pygame.math.Vector2(0,0)
        
    def custom_draw(self,player):
        target_x = player.rect.centerx - self.half_width
        target_y = player.rect.centery - self.half_height
        
        self.camera_pos.x += (target_x - self.camera_pos.x) * 0.1
        self.camera_pos.y += (target_y - self.camera_pos.y) * 0.1
        
        #getting offset
        self.offset = self.camera_pos

        for sprite in self.sprites():
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image,offset_pos)
        