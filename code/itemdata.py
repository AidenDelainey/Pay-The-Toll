import pygame

##### items #####

class Item:
    def __init__(self, item_id, data):
        self.id = item_id
        self.name = data["name"]
        self.description = data["description"]
        self.type = data["type"]
        self.stat_bonus = data.get("stats", {})
        self.sprite = data.get("sprite")
        self.stackable = data.get("stackable", False)
        self.quantity = 1
        
class WorldItem(pygame.sprite.Sprite):
    def __init__(self, pos, item_data, groups):
        super().__init__(groups)
        
        self.item_data = item_data
        
        self.image = pygame.Surface((32,32))
        self.image.fill((200, 180, 50))
        
        self.rect = self.image.get_rect(topleft=pos)
        
ITEM_DATABASE = {
    
    "test_weapon": {
        "name": "TESTW",
        "description": "TEST ALMIGHTY WEAPON",
        "type": "weapon",
        "stats": {"attack": 999},
        "stackable": False,
        "sprite": "not implemneted",
        }
    ,
    "test_spell": {
    "name": "TESTS",
        "description": "TEST ALMIGHTY SPELL",
        "type": "spell",
        "stats": {"spell": 999},
        "stackable": False,
        "sprite": "not implemneted",
        }
    ,
    "test_acc_heal": {
    "name": "TESTAH",
        "description": "TEST ALMIGHTY HEAL",
        "type": "accessory",
        "stats": {"healing": 999},
        "stackable": False,
        "sprite": "not implemneted",
        }
    ,
    "test_acc_def": {
    "name": "TESTAD",
        "description": "TEST ALMIGHTY DEFENCE",
        "type": "accessory",
        "stats": {"defence": 999},
        "stackable": False,
        "sprite": "not implemneted",
        }
    ,
    "test_acc_health": {
    "name": "TESTAHP",
        "description": "TEST ALMIGHTY HEALTH",
        "type": "accessory",
        "stats": {"health": 999},
        "stackable": False,
        "sprite": "not implemneted",
        }
    ,
    "flimsy_dagger": {
        "name": "Flimsy Dagger",
        "description": "A very basic dagger. + 3 ATK",
        "type": "weapon",
        "stats": {"attack": 5},
        "stackable": False,
        "sprite": "not implemented",
        }

    }