##### basic map ######
import pygame
from settings import *
from tile import Tile
from itemdata import WorldItem, Item, ITEM_DATABASE
from playerdata import Player
from inventory import Inventory
from debug import debug



class Level:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.item_sprites = pygame.sprite.Group()
        self.visable_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()
        
        self.create_map()
        
        self.inventory = Inventory(self.player)
        self.inventory_open = False
        
    def handle_input(self, event):
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_TAB:
                self.inventory_open = not self.inventory_open
                
            if self.inventory_open:
                self.inventory.handle_input(event)
        
    def create_map(self):
        for row_index,row in enumerate(WORLD_MAP):
            for col_index, col in enumerate(row):
                x = col_index * TILESIZE
                y = row_index * TILESIZE
                if col == 'x':
                    Tile((x,y),[self.visable_sprites,self.obstacle_sprites])
                if col == 'p':
                    self.player = Player((x,y),[self.visable_sprites],self.obstacle_sprites)
                if col == 'i':
                    dagger_item = Item("dagger", ITEM_DATABASE["flimsy_dagger"])
                    WorldItem((x, y), dagger_item, [self.visable_sprites, self.item_sprites])
                if col == 't':
                    test_item = Item("test", ITEM_DATABASE["test_weapon"])
                    WorldItem((x,y), test_item, [self.visable_sprites, self.item_sprites])
                if col == 's':
                    test_s = Item("test", ITEM_DATABASE["test_spell"])
                    WorldItem((x, y), test_s, [self.visable_sprites, self.item_sprites])
                if col == "h":
                    test_ah = Item("test", ITEM_DATABASE["test_acc_heal"])
                    WorldItem((x, y), test_ah, [self.visable_sprites, self.item_sprites])
                if col == "d":
                    test_ad = Item("test", ITEM_DATABASE["test_acc_def"])
                    WorldItem((x, y), test_ad, [self.visable_sprites, self.item_sprites])
    def run(self):
        self.visable_sprites.custom_draw(self.player)

        if not self.inventory_open:
            self.visable_sprites.update()
            
            collided_items = pygame.sprite.spritecollide(self.player, self.item_sprites, True)
            for item_sprite in collided_items:
                self.inventory.add_item(item_sprite.item_data)
            
        if self.inventory_open:
            self.inventory.draw()
        
class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()
        
    def custom_draw(self,player):
        #getting offset
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height
        
        for sprite in self.sprites():
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image,offset_pos)
        