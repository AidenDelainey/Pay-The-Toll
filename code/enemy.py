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

        self.load_sprites()
        self.image = self.sprites["idle"]

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
        self.facing_left = False
        
        self.last_pos = pygame.math.Vector2(self.rect.center)
        self.stuck_timer = 0
        
    def load_sprites(self):
        enemy_path = os.path.join(enemies_path, self.enemy_id)
        
        self.sprites = {
            "idle": pygame.image.load(os.path.join(enemy_path, "idle.png")).convert_alpha(),
            "dead": pygame.image.load(os.path.join(enemy_path, "dead.png")).convert_alpha()
        }
        
        for key in self.sprites:
            self.sprites[key] = pygame.transform.scale(self.sprites[key],(TILESIZE, TILESIZE))
        

    def get_new_target(self):
        for _ in range(10):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, self.roam_radius)
            
            offset = pygame.math.Vector2(
                math.cos(angle) * distance,
                math.sin(angle) * distance
            )
            
            target = self.spawn_pos + offset
            test_rect = self.rect.copy()
            test_rect.center = target
            
            blocked = False
            for sprite in self.obstacle_sprites:
                if sprite.rect.colliderect(test_rect):
                    blocked = True
                    break
            if not blocked:
                return target
            
        return self.spawn_pos
        
    def get_nearby_enemies(self, radius=300, max_enemies=3):
        nearby = [self]

        for enemy in self.level.enemy_sprites:
            if enemy is self:
                continue
            if not enemy.alive or enemy.in_combat:
                continue

            dist = pygame.math.Vector2(enemy.rect.center).distance_to(self.rect.center)

            if dist <= radius:
                nearby.append(enemy)

            if len(nearby) >= max_enemies:
                break

        return nearby

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
        self.collision("horizontal")
        self.rect.y += self.direction.y * self.speed
        self.collision("vertical")
        
    def collision(self, direction):
        for sprite in self.obstacle_sprites:
            if sprite.rect.colliderect(self.rect):
                
                if direction == "horizontal":
                    if self.direction.x > 0:  # moving right
                        self.rect.right = sprite.rect.left
                    if self.direction.x < 0:  # moving left
                        self.rect.left = sprite.rect.right

                    self.velocity.x = 0  # stop sliding into wall

                if direction == "vertical":
                    if self.direction.y > 0:  # moving down
                        self.rect.bottom = sprite.rect.top
                    if self.direction.y < 0:  # moving up
                        self.rect.top = sprite.rect.bottom

                    self.velocity.y = 0

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

        enemies = self.get_nearby_enemies()
        for enemy in enemies:
            enemy.in_combat = True
            enemy.state = "IN_COMBAT"
            
        self.level.combat = CombatSystem(self.player, enemies)
        
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
            #self.player.current_health = 10
            
            self.state = "ROAMING"
    
    def become_corpse(self):
        self.alive = False
        self.state = "DEAD"
        self.direction = pygame.math.Vector2()

        self.image = self.sprites["dead"]

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
            
        current_pos = pygame.math.Vector2(self.rect.center)
        
        if current_pos.distance_to(self.last_pos) < 1:
            self.stuck_timer += 1
        else:
            self.stuck_timer = 0
            
        self.last_pos = current_pos
        
        if self.stuck_timer > 30:
            self.roam_target = self.get_new_target()
            self.stuck_timer = 0
        
        
        self.check_player_distance()
        if self.state == "ROAMING":
            self.roam()
        else:
            self.chase()

        self.move()
        if self.direction.x < -0.1:
            self.facing_left = True
        elif self.direction.x > 0.1:
            self.facing_left = False
            
        if self.state != "DEAD":
            if self.facing_left:
                self.image = pygame.transform.flip(self.sprites["idle"], True, False)
            else:
                self.image = self.sprites["idle"]
        
        
        self.check_collision()

ENEMY_DATABASE = {
    
    "soilder": {
        "name": "Soilder",
        "health": 40,
        "attack": 5,
        "defence": 3,
        "resistance": {
            "physical": 0.1,
            "spell": 0.3
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
        "attack": 2,
        "defence": 0,
        "resistance": {
            "physical": 0.0,
            "spell": 0.0
        },
        "speed": 5,
        "detection": 200,
        "roam": 5,
        "sprite": "not implemented"
    }
    ,
    "zombie": {
        "name": "Zombie",
        "health": 40,
        "attack": 3,
        "defence": 2,
        "resistance": {
            "physical": -0.4,
            "spell": 0.4
        },
        "speed": 2,
        "detection": 200,
        "roam": 5,
        "sprite": "not implemented"
    }
    ,
    "royal_soilder": {
        "name": "Royal Soilder",
        "health": 50,
        "attack": 10,
        "defence": 4,
        "resistance": {
            "physical": 0.2,
            "spell": 0.4
        },
        "speed": 4,
        "detection": 300,
        "roam": 2,
        "sprite": "not implemented"
    }
    ,
    "gnome": {
        "name": "GNOME",
        "health": 250,
        "attack": 12,
        "defence": 4,
        "resistance": {
            "physical": 0.5,
            "spell": -0.2
        },
        "speed": 0,
        "detection": 0,
        "roam": 0,
        "sprite": "not implemented"
    }
    ,
}
        
        

