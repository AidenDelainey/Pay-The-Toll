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
    # Melee Items #
    "dagger": {
        "name": "Dagger",
        "description": "Possible a murder weapon but its yours now +2 ATK",
        "type": "weapon",
        "stats": {"attack": 2},
        "stackable": False,
        }
    ,
    "sword": {
        "name": "Iron Sword",
        "description": "A standerd issue sword for soilders +4 ATK",
        "type": "weapon",
        "stats": {"attack": 4},
        "stackable": False,
        }
    ,
    "metal_fisters": {
        "name": " Metal Fisters",
        "description": "'crack' 'crack' ITS FISTING TIME +6 ATK +2 DEF",
        "type": "weapon",
        "stats": {"attack": 6,
                  "defence": 2},
        "stackable": False,
        }
    ,
    "stick": {
        "name": "Stick",
        "description": "Its just a stick, no magic +1 ATK",
        "type": "weapon",
        "stats": {"attack": 1},
        "stackable": False,
        }
    ,
    "excaliber": {
        "name": "Excaliber",
        "description": "How was this made from a stick +10 ATK +3 DEF +10 HP",
        "type": "weapon",
        "stats": {"attack": 10,
                  "defence": 3,
                  "health": 10},
        "stackable": False,
        }
    ,
    # Spell Items #
    "wand": {
        "name": "Wooden Wand",
        "description": "Its a stick, but magic + 2SPL +1 HEL",
        "type": "spell",
        "stats": {"spell": 2,
                  "healing": 1},
        "stackable": False,
        }
    ,
    "staff": {
        "name": "Staff",
        "description": "A long stick with an orb made of something +4 SPL +2 HEL",
        "type": "spell",
        "stats": {"spell": 4,
                  "healing": 2},
        "stackable": False,
        }
    ,
    "tome_of_fireball": {
        "name": "Tome of Fireball",
        "description": "FIREBALL, FIREBALL, FIREBALL +6 SPL +2 HEL",
        "type": "spell",
        "stats": {"spell": 6,
                  "healing": 2},
        "stackable": False,
        }
    ,
    "tome_of_greater_spells": {
        "name": "Tome of Greater Spells,(NOW WITH FIREBALL)",
        "description": "It has more spells and is purple +7 SPL +2 HEL",
        "type": "spell",
        "stats": {"spell": 7,
                  "healing": 2},
        "stackable": False,
        }
    ,
    "orb_of_chaos": {
        "name": "Orb of Chaos",
        "description": "Blue orb +10 SPL +4 HEL",
        "type": "spell",
        "stats": {"spell": 10,
                  "healing": 4},
        "stackable": False,
        }
    ,
    # Melee Acc #
    "sharpening_stone": {
        "name": "Sharpening Stone",
        "description": "A coarse rock that can sharpen your equipment +2 ATK",
        "type": "accessory",
        "stats": {"attack": 2},
        "stackable": False,
        }
    ,
    "rune_of_blood": {
        "name": "Rune of Blood",
        "description": "A stone with a bloody sigil cut into it +4 ATK +5 HP",
        "type": "accessory",
        "stats": {"attack": 4,
                  "health": 5},
        "stackable": False,
        }
    ,
    "arm_bracer": {
        "name": "Arm Bracers ",
        "description": "A pair of bracers that allow more precise slashing +8 ATK +3 DEF",
        "type": "accessory",
        "stats": {"attack": 8,
                  "defence": 3},
        "stackable": False,
        }
    ,
    "warriors_medalion": {
        "name": "Warriors Medalion",
        "description": "A small coin that somehow makes you stonger +10 ATK +10 HP +5 DEF",
        "type": "accessory",
        "stats": {"attack": 10,
                  "health": 10,
                  "defence": 5},
        "stackable": False,
        }
    ,
    # Healing Acc #
    "silver_ring": {
        "name": "Silver Ring",
        "description": "A ring made of silver +3 HEL",
        "type": "accessory",
        "stats": {"healing": 3},
        "stackable": False,
        }
    ,
     "gold_ring": {
        "name": "Gold Ring",
        "description": "S	omehow more powerful then silver +5 HEL",
        "type": "accessory",
        "stats": {"healing": 5},
        "stackable": False,
        }
    ,
     "tome_of_healing": {
        "name": "Tome of Healing",
        "description": "Decpit what you think this is an accessory +6 HEL +5 HP",
        "type": "accessory",
        "stats": {"healing": 6,
                  "health": 5},
        "stackable": False,
        }
    ,
     "clerics_cross": {
        "name": "Cleric Cross",
        "description": "The only time religion is useful +8 HEL",
        "type": "accessory",
        "stats": {"healing": 8},
        "stackable": False,
        }
    ,
    # Magic Acc #
    "novice_cloak": {
        "name": "Novice Cloak",
        "description": "A cloak with basic magic in its cloth +2 SPL",
        "type": "accessory",
        "stats": {"spell": 2},
        "stackable": False,
        }
    ,
    "apprentice_cloak": {
        "name": "Appretice Cloak",
        "description": "A cloak with more complex magic +4 SPL",
        "type": "accessory",
        "stats": {"spell": 4},
        "stackable": False,
        }
    ,
    "master_cloak": {
        "name": "Masters Cloak",
        "description": "A cloak with a decent amount of magic +6 SPL",
        "type": "accessory",
        "stats": {"spell": 6},
        "stackable": False,
        }
    ,
    "scroll_of_power": {
        "name": "Scroll of Power",
        "description": "A scroll that is more powerful then the cloak you might be wearing +8 SPL",
        "type": "accessory",
        "stats": {"spell": 8},
        "stackable": False,
        }
    ,
    # Misc Acc #
    "lesser_vitality": {
        "name": "Vial of Lesser Vitality",
        "description": "A small vial filled with a red liquid +10 HP",
        "type": "accessory",
        "stats": {"health": 10},
        "stackable": False,
        }
    ,
    "greater_vitality": {
        "name": "Flask of greater Vitality",
        "description": "Like the lesser vial but bigger +20 HP",
        "type": "accessory",
        "stats": {"health": 20},
        "stackable": False,
        }
    ,
    "sheild": {
        "name": "Sheid",
        "description": "Not sure how you can use this with two handed weapons +5 DEF +10 HP",
        "type": "accessory",
        "stats": {"defence": 5,
                  "health": 10},
        "stackable": False,
        }
    ,

    }