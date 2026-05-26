import pygame

##### items #####

class Item:
    def __init__(self, item_id, data, image=None):
        self.id = item_id
        self.name = data["name"]
        self.description = data["description"]
        self.type = data["type"]
        self.stat_bonus = data.get("stats", {})
        self.sprite = data.get("sprite")
        self.stackable = data.get("stackable", False)
        self.quantity = 1
        
        self.image = image
        
class WorldItem(pygame.sprite.Sprite):
    def __init__(self, pos, item_data, groups, image=None):
        super().__init__(groups)
        
        self.item_data = item_data
        
        if image:
            self.image = pygame.transform.scale(image, (64,64))
        else:
            self.image = pygame.Surface((32,32))
            self.image.fill((200, 180, 50))
        
        self.rect = self.image.get_rect(topleft=pos)
        
ITEM_DATABASE = {
    "template": {
        "name": " ",
        "description": " ",
        "type": " ",
        "stats": {},
        "stackable": False,
        }
    ,
    "test_weapon": {
        "name": "TESTW",
        "description": "TEST ALMIGHTY WEAPON",
        "type": "weapon",
        "stats": {"attack": 999},
        "stackable": False,
        }
    ,
    "test_spell": {
    "name": "TESTS",
        "description": "TEST ALMIGHTY SPELL",
        "type": "spell",
        "stats": {"spell": 999},
        "stackable": False,
        }
    ,
    "test_acc_heal": {
    "name": "TESTAH",
        "description": "TEST ALMIGHTY HEAL",
        "type": "accessory",
        "stats": {"healing": 999,
                  "spell": 999},
        "stackable": False,
        }
    ,
    "test_acc_def": {
    "name": "TESTAD",
        "description": "TEST ALMIGHTY DEFENCE",
        "type": "accessory",
        "stats": {"defence": 999},
        "stackable": False,
        }
    ,
    "test_acc_health": {
    "name": "TESTAHP",
        "description": "TEST ALMIGHTY HEALTH",
        "type": "accessory",
        "stats": {"health": 999},
        "stackable": False,
        }
    ,
    "flimsy_dagger": {
        "name": "Flimsy Dagger",
        "description": "A very basic dagger. +3 ATK",
        "type": "weapon",
        "stats": {"attack": 3},
        "stackable": False,
        }
    ,
    "wooden_wand": {
        "name": "Wooden Wand",
        "description": "Its a stick, but magic + 2 SPL +1 HEL",
        "type": "spell",
        "stats": {"spell": 2,
                  "healing": 1},
        "stackable": False,
        }
    ,
    "simple_bracers": {
        "name": "Simple Bracers ",
        "description": "A simple pair of bracers +3 DEF +5 HP",
        "type": "accessory",
        "stats": {"defence": 3,
                  "health": 5},
        "stackable": False,
        }
    ,
    "silver_ring": {
        "name": "Silver Ring",
        "description": "A ring made of silver +3 HEL",
        "type": "accessory",
        "stats": {"healing": 3},
        "stackable": False,
        }
    ,
    "apprentice_cloak": {
        "name": "Appretice's Cloak",
        "description": "A cloak with basic magic imbude in its cloth +2 SPL",
        "type": "accessory",
        "stats": {"spell": 2},
        "stackable": False,
        }
    ,
    "metal_fisters": {
        "name": " Metal Fisters",
        "description": "'crack' 'crack' ITS FISTING TIME +5 ATK +2 DEF",
        "type": "weapon",
        "stats": {"attack": 5,
                  "defence": 2},
        "stackable": False,
        }
    ,
    "enchanted_drums": {
        "name": "Enchanted Drums",
        "description": "The drums beats reasonate with magical power +3 SPL +2 HEL",
        "type": "accessory",
        "stats": {"spell": 3,
                  "healing": 2},
        "stackable": False,
        }
    ,
    "wooden_staff": {
        "name": "Wooden Staff",
        "description": "Its better then a stick +4 SPL +2 HEL",
        "type": "spell",
        "stats": {"spell": 4,
                  "healing": 2},
        "stackable": False,
        }
    ,
    "wing_sword": {
        "name": "Wing Sword",
        "description": "A feather like sword that can launch enemies away +6 ATK",
        "type": "weapon",
        "stats": {"attack": 6},
        "stackable": False,
        }
    ,
    }