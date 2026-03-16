class Enemy:
    def __init__(self, enemy_id):
        
        data = ENEMY_DATABASE[enemy_id]
        
        self.name = data["name"]
        
        self.health = data["health"]
        self.max_health = data["health"]
        
        self.attack = data["attack"]
        self.defence = data["defence"]
        
        self.resistance = data["resistance"]
        
ENEMY_DATABASE = {
    
    "tainted": {
        "name": "Tainted",
        "health": 20,
        "attack": 4,
        "defence": 1,
        "resistance": {
            "physical": 0.10,
            "spell": 0.0
        },
        "sprite": "not implemented"
    }
    
    ,
}
        
        

