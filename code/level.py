##### basic map ######
import pygame
from settings import *
from tile import Tile
from itemdata import WorldItem, Item, ITEM_DATABASE
from combat import CombatSystem
from playerdata import Player
from enemy import Enemy
from inventory import Inventory
from pytmx.util_pygame import load_pygame

tmx_data = load_pygame('../map/test.tmx')
menu_music = (os.path.join(sound_path, "menu music.mp3"))
combat_music = (os.path.join(sound_path, "combat music.mp3"))

ITEM_FONT = pygame.font.Font(font_path, 24)
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
        
        self.nearby_item = None
        self.ITEM_FONT = pygame.font.Font(font_path, 24)
        
        self.game_state = "explore"
        
        pygame.mixer.music.load(menu_music)
        pygame.mixer.music.play(-1)
        
    def handle_input(self, event):
        
        if self.game_state == "combat" and self.combat:
            self.combat.handle_input(event)
            return

        if event.type == pygame.KEYUP and event.key == pygame.K_TAB:
            self.inventory_open = not self.inventory_open

            if self.inventory_open:
                inv_open_snd.play()
            else:
                inv_close_snd.play()

        if event.type == pygame.KEYDOWN:
            
            if event.key == pygame.K_f:
                self.enemy = Enemy("tainted")
                self.combat = CombatSystem(self.player, self.enemy)
                self.game_state = "combat"
                pygame.mixer.music.load(combat_music)
                pygame.mixer.music.play(-1)

            if event.key == pygame.K_e and self.nearby_item:
                self.inventory.add_item(self.nearby_item.item_data)
                self.nearby_item.kill()
                self.nearby_item = None

        if self.inventory_open:
            self.inventory.handle_input(event)
            
        
    def create_map(self):
        for layer in tmx_data.visible_layers:
            if hasattr(layer, 'data'):
                for x, y, surf in layer.tiles():
                   pos =  (x * 64, y * 64)
                   Tile(pos, surf, self.visable_sprites)
        for layer in tmx_data.layers:
            if layer.name in ('collisoins'):
                for x, y, surf in layer.tiles():
                    pos = (x * 64, y * 64)
                    Tile(pos, surf, self.obstacle_sprites)
            if layer.name in  ('item'):
                for x, y, gid in layer:
                    if gid == 0:
                        continue
                    
                    tile_props = tmx_data.get_tile_properties_by_gid(gid)
                    
                    if tile_props and "item" in tile_props:
                        item_key = tile_props["item"]
                        
                        if item_key in ITEM_DATABASE:
                            pos = (x * 64, y * 64)
                            
                            item = Item(item_key, ITEM_DATABASE[item_key])
                            image = tmx_data.get_tile_image_by_gid(gid)
                            WorldItem(pos, item, [self.visable_sprites, self.item_sprites], image)
            if layer.name in ('player'):
                for x, y, surf in layer.tiles():
                    pos = (x * 64, y * 64)
                    self.player = Player(pos,[self.visable_sprites],self.obstacle_sprites)
            if layer.name in ('Objects'):
                for x, y, surf in layer.tiles():
                    pos = (x * 64, y * 64)
                    Tile(pos, surf, self.visable_sprites)
                
    def run(self):
        if self.game_state == "explore":
            self.visable_sprites.custom_draw(self.player)

            if not self.inventory_open:
                self.visable_sprites.update()

                nearby_items = pygame.sprite.spritecollide(
                    self.player,
                    self.item_sprites,
                    False
                )

                if nearby_items:
                    self.nearby_item = nearby_items[0]
                else:
                    self.nearby_item = None
                
            if self.inventory_open:
                self.inventory.draw()
                
            if self.nearby_item:
                text = self.ITEM_FONT.render("Press E to pick up", True, (255,255,255))
                offset_pos = self.nearby_item.rect.topleft - self.visable_sprites.offset
                text_rect = text.get_rect(midbottom=(offset_pos.x + 16, offset_pos.y - 5))
                self.display_surface.blit(text, text_rect)
                
        elif self.game_state == "combat":
            if self.combat:
                self.combat.update()
                self.combat.draw(self.display_surface)
            
                if self.combat.finished:
                    self.game_state = "explore"
                    self.combat = None
                    pygame.mixer.music.load(menu_music)
                    pygame.mixer.music.play(-1)
        
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
        