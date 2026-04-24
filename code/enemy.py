import pygame
from settings import *
import random
import math
from combat import CombatSystem
    
class WorldEnemy(pygame.sprite.Sprite):
    def __init__(self, pos, enemy_id, groups, obstacle_sprites, player, level):
        super().__init__(groups)
        
        self.y_sort = False
        self.level = level
        self.player = player
        self.obstacle_sprites = obstacle_sprites
        
        self.in_combat = False

        data = ENEMY_DATABASE[enemy_id]
        self.enemy_id = enemy_id

        self.name = data["name"]
        self.max_health = data["health"]
        self.health = data["health"]
        self.attack = data["attack"]
        self.defence = data["defence"]
        self.resistance = data["resistance"]
        self.speed = data["speed"]
        self.detection_radius = data["detection"]
        self.roam_area = data["roam"]

        self.image = pygame.Surface((TILESIZE, TILESIZE))
        self.image.fill((200, 50, 50))  # placeholder

        self.rect = self.image.get_rect(topleft=pos)

        self.direction = pygame.math.Vector2()
        self.velocity = pygame.math.Vector2()
        self.idle_timer = 0

        self.alive = True
        self.state = "ROAMING"

        self.spawn_pos = pygame.math.Vector2(pos)
        self.roam_radius = self.roam_area * TILESIZE
        self.roam_target = self.get_new_target()
        
        self.combat_cooldown = 0
        self.immunity_time = 0
        self.immunity_duration = 60
        

    def get_new_target(self):
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0, self.roam_radius)
        
        offset_x = math.cos(angle) * distance
        offset_y = math.sin(angle) * distance
        return self.spawn_pos + pygame.math.Vector2(offset_x, offset_y)

    def check_player_distance(self):
        enemy_pos = pygame.math.Vector2(self.rect.center)
        player_pos = pygame.math.Vector2(self.player.rect.center)
        
        distance = enemy_pos.distance_to(player_pos)

        if distance < self.detection_radius and self.immunity_time == 0:
            self.state = "CHASING"
        else:
            self.state = "ROAMING"

    def roam(self):
        if self.idle_timer > 0:
            self.idle_timer -=1
            
            self.velocity *= 0.85
            if self.velocity.length() < 0.05:
                self.velocity = pygame.math.Vector2()  
            self.direciton = self.velocity
            return
        
        desired = self.roam_target - pygame.math.Vector2(self.rect.center)
        if desired.length() > 5:
            desired = desired.normalize()
        else:
            self.roam_target = self.get_new_target()
            self.idle_timer = random.randint(30, 120)
            desired = self.velocity
            
        self.velocity = self.velocity.lerp(desired, 0.05)
        self.direction = self.velocity

    def chase(self):
        direction = pygame.math.Vector2(self.player.rect.center) - pygame.math.Vector2(self.rect.center)

        if direction.length() > 0:
            self.direction = direction.normalize()

    def move(self):
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

    def check_collision(self):
        if self.in_combat:
            return
        if self.immunity_time > 0:
            return
        
        if self.combat_cooldown <= 0 and self.rect.colliderect(self.player.rect):
            self.start_combat()

    def start_combat(self):
        if self.in_combat:
            return
        
        self.in_combat = True
        self.state = "IN_COMBAT"
        
        self.combat_cooldown = 60

        self.level.combat = CombatSystem(self.player, self)
        self.level.game_state = "combat"
        
        self.level.start_combat_music()
        
    def exit_combat(self, result):
        self.in_combat = False

        self.immunity_time = self.immunity_duration
        self.combat_cooldown = 30
        
        if result == "win":
            self.alive = False
            self.state = "DEAD"
            self.become_corpse()
            self.direction = pygame.math.Vector2()
            return

        if result == "run":
            direction = pygame.math.Vector2(self.rect.center) - pygame.math.Vector2(self.player.rect.center)
            
            if direction.length() == 0:
                direction = pygame.math.Vector2(random.uniform(-1,1), random.uniform(-1,1))
                
            direction = direction.normalize()
            
            if self.speed > 0:
                knockback_distance = TILESIZE * 2.5
                self.rect.center += direction * knockback_distance
            
            self.state = "ROAMING"
            self.roam_target = self.get_new_target()
            self.direction = pygame.math.Vector2()
            return
        
        elif result == "lose":
            self.player.rect.topleft = self.player.spawn_pos
            
            self.state = "ROAMING"
    
    def become_corpse(self):
        self.alive = False
        self.state = "DEAD"
        self.direction = pygame.math.Vector2()

        # visual change (simple corpse)
        self.image.fill((80, 80, 80))

    def update(self):
        if self.state == "DEAD":
            return
        if self.in_combat:
            return
        
        if self.combat_cooldown > 0:
            self.combat_cooldown -= 1
        
        if self.immunity_time > 0:
            self.immunity_time -= 1
            self.direction = pygame.math.Vector2()
        
        self.check_player_distance()
        if self.state == "ROAMING":
            self.roam()
        else:
            self.chase()

        self.move()
        self.check_collision()

ENEMY_DATABASE = {
    
    "soilder": {
        "name": "Soilder",
        "health": 40,
        "attack": 4,
        "defence": 1,
        "resistance": {
            "physical": 0.1,
            "spell": 0.0
        },
        "speed": 3,
        "detection": 250,
        "roam": 3,
        "sprite": "not implemented"
    }
    ,
    "skeleton": {
        "name": "Skeleton",
        "health": 15,
        "attack": 4,
        "defence": 2,
        "resistance": {
            "physical": 0.0,
            "spell": 0.5
        },
        "speed": 5,
        "detection": 200,
        "roam": 5,
        "sprite": "not implemented"
    }
    ,
}
        
        

