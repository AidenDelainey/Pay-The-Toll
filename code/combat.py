# combat #
import pygame
from settings import *
import random

pygame.init()

select_snd = pygame.mixer.Sound(os.path.join(sound_path, "item hover.mp3"))
weapon_swing_snd = pygame.mixer.Sound(os.path.join(combat_path, "weapon swing.mp3"))
immune_hit_snd = pygame.mixer.Sound(os.path.join(combat_path, "immune hit.mp3"))
resist_hit_snd = pygame.mixer.Sound(os.path.join(combat_path, "strong hit.mp3"))
weak_hit_snd = pygame.mixer.Sound(os.path.join(combat_path, "weak hit.mp3"))
normal_hit_snd = pygame.mixer.Sound(os.path.join(combat_path, "normal hit.mp3"))
spell_cast_snd = pygame.mixer.Sound(os.path.join(combat_path, "spell cast.mp3"))
heal_spell_snd = pygame.mixer.Sound(os.path.join(combat_path, "heal spell.mp3"))
marker_hit_snd = pygame.mixer.Sound(os.path.join(combat_path, "marker hit.mp3"))

class CombatSystem:
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy
        
        self.turn = "player"
        self.state = "PLAYER_MENU"
        self.finished = False
        
        self.font = pygame.font.Font(font_path, 24)
        
        self.options = ["Attack", "Spell", "Heal", "Run"]
        self.selected_option = 0
        
        self.enemy_turn_delay = 800
        self.enemy_turn_start = None
        
        self.max_heals = 3
        self.heals_used = 0
        
        self.spell_power = 1
        self.spell_hits = 0
        self.max_spell_hits = 5
        
        self.bar_pos = 0
        self.bar_speed = 0
        self.target_pos = 0
        self.target_width = 0.1
        self.safe_zone = 0
        self.safe_width = 0.15
        
        self.result = None
        
    
    def player_heal(self):
        
        if self.heals_used >= self.max_heals:
            return
        
        heal = self.player.get_stat("healing") + roll_dice(4)
        heal_spell_snd.play()
        
        self.player.current_health = min(
            self.player.current_health + heal,
            self.player.max_hp
        )
        self.heals_used += 1
        
        
    def player_run(self):
        self.result = "run"
        self.finished = True
         
    def update_bar(self):
        self.bar_pos += self.bar_speed
        
        if self.state == "ATTACK_MINIGAME":
            if self.bar_pos >= 1:
                self.bar_pos = 1
                self.confirm_attack(missed=True)
        else:
            if self.bar_pos >=1 or self.bar_pos <= 0:
                self.bar_speed *= -1
            
    def start_attack_minigame(self):
        self.state = "ATTACK_MINIGAME"
        
        self.bar_pos = 0
        self.bar_speed = random.choice([0.012, 0.015, 0.02])
        
        self.target_pos = random.uniform(0.15, 0.85)
        self.target_width = 0.12
        
    def confirm_attack(self, missed=False):
        if missed:
            accuracy = 0
            self.resolve_attack(accuracy, missed=True)
            return
        
        distance = abs(self.bar_pos - self.target_pos)
        accuracy = max(0, 1 -(distance / self.target_width))
        self.resolve_attack(accuracy, missed=False)
       
    def resolve_attack(self, accuracy, missed=False):
        if missed or accuracy <= 0:
            weapon_swing_snd.play()
            
            self.turn = "enemy"
            self.enemy_turn_start = pygame.time.get_ticks()
            self.state = "WAITING"
            return
        
        
        base_attack = self.player.get_stat("attack")
        dice_roll = roll_dice(4)
        raw = base_attack + dice_roll
        
        multiplier = 0.5 + (accuracy * 1.5)
        damage = int(raw * multiplier)
        
        resist = self.enemy.resistance.get("physical", 0)
        final_damage = max(0, int(damage * (1-resist) - self.enemy.defence))
        
        self.enemy.health = max(0, self.enemy.health - final_damage)
        
        weapon_swing_snd.play()
        if final_damage == 0:
            immune_hit_snd.play()
        elif resist > 0:
            resist_hit_snd.play()
        elif resist < 0:
            weak_hit_snd.play()
        else:
            normal_hit_snd.play()
        
        self.turn = "enemy"
        self.enemy_turn_start = pygame.time.get_ticks()
        self.state = "WAITING"
        
    def start_spell_minigame(self):
        self.state = "SPELL_MINIGAME"
        
        self.bar_pos = 0
        self.bar_speed = random.choice([0.015, 0.02])
        
        self.target_pos = random.uniform(0.2, 0.8)
        self.target_width = 0.12
        
        self.spell_power = 1
        self.spell_hits = 0
        
    def confirm_spell(self):
        distance = abs(self.bar_pos - self.target_pos)
        accuracy = max(0, 1 - (distance / self.target_width))
        
        if accuracy <= 0:
            self.resolve_spell()
            return
        
        self.spell_hits += 1
        self.spell_power += accuracy * 0.5
        marker_hit_snd.play()
        
        if self.spell_hits >= self.max_spell_hits:
            self.resolve_spell()
            return
        self.bar_speed *= random.choice([1.1, 1.5])
        self.target_pos = random.uniform(0.2, 0.8)
        
    def resolve_spell(self):
        base_attack = self.player.get_stat("spell")
        dice = roll_dice(6)
        raw = base_attack + dice
        damage = int(raw * self.spell_power)
        resist = self.enemy.resistance.get("spell", 0)
        final_damage = int(damage * (1 - resist))
        
        self.enemy.health = max(0, self.enemy.health - final_damage)
        spell_cast_snd.play()
        
        self.turn = "enemy"
        self.enemy_turn_start = pygame.time.get_ticks()
        self.state = "WAITING"
        
    def start_dodge_minigame(self):
        self.state = "DODGE_MINIGAME"
        
        self.bar_pos = 0
        self.bar_speed = random.choice([0.015, 0.02, 0.025])
        self.safe_zone = random.uniform(0.2, 0.8)
        self.safe_width = 0.05
        
    def confirm_dodge(self):
        distance = abs(self.bar_pos - self.safe_zone)
        accuracy = max(0, 1 - (distance / self.safe_width))
        
        self.resolve_enemy_attack(accuracy)
        
        
    def resolve_enemy_attack(self, accuracy):
        dice = roll_dice(4)
        raw = self.enemy.attack + dice
        
        reduction = accuracy * 0.5
        damage = int(raw * (1 - reduction) - self.player.get_stat("defence"))
        damage = max(0, damage)
        
        self.player.current_health = max(0, self.player.current_health - damage)
        
        weapon_swing_snd.play()
        
        self.turn = "player"
        self.state = "PLAYER_MENU"
        
    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return

        # ===== PLAYER MENU =====
        if self.state == "PLAYER_MENU":

            if event.key == pygame.K_a:
                self.selected_option = (self.selected_option - 1) % len(self.options)
                select_snd.play()

            elif event.key == pygame.K_d:
                self.selected_option = (self.selected_option + 1) % len(self.options)
                select_snd.play()

            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):

                if self.selected_option == 0:
                    self.start_attack_minigame()

                elif self.selected_option == 1:
                    self.start_spell_minigame()

                elif self.selected_option == 2:
                    self.player_heal()

                elif self.selected_option == 3:
                    self.player_run()

        elif self.state == "ATTACK_MINIGAME":
            if event.key == pygame.K_SPACE:
                self.confirm_attack()

        elif self.state == "DODGE_MINIGAME":
            if event.key == pygame.K_SPACE:
                self.confirm_dodge()
                
        elif self.state == "SPELL_MINIGAME":
            if event.key == pygame.K_SPACE:
                self.confirm_spell()
                    
    def update(self):
        if self.enemy.health <= 0:
            self.result = "win"
            self.finished = True
            return
            
        if self.player.current_health <= 0:
            self.result = "lose"
            self.finished = True
            return
        
        if self.state in ("ATTACK_MINIGAME", "DODGE_MINIGAME", "SPELL_MINIGAME"):
            self.update_bar()
            
        if self.turn == "enemy" and not self.finished:
            now = pygame.time.get_ticks()
            
            if self.enemy_turn_start is not None and now - self.enemy_turn_start >= self.enemy_turn_delay:
                self.start_dodge_minigame()
                self.enemy_turn_start = None
            
    def draw_health_bar(self, surface,x,y,width,height,current,maxhp):
        ratio = current/maxhp
        pygame.draw.rect(surface,(0,0,0),(x-2,y-2,width+4,height+4))
        pygame.draw.rect(surface,(120,0,0),(x,y,width,height))
        pygame.draw.rect(
            surface,
            (255,50,50),
            (x,y,width*ratio,height)
        )
        
        hp_text = self.font.render(f"{current} / {maxhp}", True, (255,255,255))
        text_rect = hp_text.get_rect(center=(x + width//2, y + height + 15))
        surface.blit(hp_text, text_rect)
        
    def draw_bar(self, surface, target, width_ratio):
        width, height = surface.get_size()

        bar_rect = pygame.Rect(width//2 - 200, height//2, 400, 20)
        pygame.draw.rect(surface, (100, 100, 100), bar_rect)

        target_x = bar_rect.x + int(target * bar_rect.width)
        target_w = int(width_ratio * bar_rect.width)
        pygame.draw.rect(surface, (255, 200, 50),
                         (target_x, bar_rect.y, target_w, bar_rect.height))

        cursor_x = bar_rect.x + int(self.bar_pos * bar_rect.width)
        pygame.draw.rect(surface, (255, 255, 255),
                         (cursor_x, bar_rect.y - 5, 4, bar_rect.height + 10))

    def draw_buttons(self, surface):
        width, height = surface.get_size()

        button_y = height - 220
        button_w = 140
        button_h = 50

        font = pygame.font.Font(None,32)
        for i, text in enumerate(self.options):
            x = 60 + i * (button_w + 20)
            rect = pygame.Rect(x,button_y,button_w,button_h)

            # highlight selected
            if i == self.selected_option:
                color = (255,255,120)
                border = (255,255,255)
            else:
                color = (160,160,160)
                border = (80,80,80)

            pygame.draw.rect(surface,color,rect,border_radius=8)
            pygame.draw.rect(surface,border,rect,3,border_radius=8)
            label = font.render(text,True,(0,0,0))
            surface.blit(label,label.get_rect(center=rect.center))
                
    def draw(self, surface):
        width,height = surface.get_size()
        panel = pygame.Rect(0,height-200,width,200)
        pygame.draw.rect(surface,(120,70,20),panel)
        pygame.draw.rect(surface,(255,255,255),panel,4)
        
        heal_text = self.font.render(
            f"Heals: {self.max_heals - self.heals_used}",
            True, (255, 255, 255)
        )
        surface.blit(heal_text, (width-950, height-50))

        # health bars
        self.draw_health_bar(
            surface, 
            60, height-120,
            350, 30,
            self.player.current_health,
            self.player.max_hp
        )

        self.draw_health_bar(
            surface,
            width//2+60,height-120,
            350,30,
            self.enemy.health,
            self.enemy.max_health
        )
        
        if self.state == "ATTACK_MINIGAME":
            self.draw_bar(surface, self.target_pos, self.target_width)

        elif self.state == "DODGE_MINIGAME":
            self.draw_bar(surface, self.safe_zone, self.safe_width)
        elif self.state == "SPELL_MINIGAME":
            self.draw_bar(surface, self.target_pos, self.target_width)

        # labels
        ptext = self.font.render("You",True,(0,0,0))
        etext = self.font.render(self.enemy.name,True,(0,0,0))
        surface.blit(ptext,(60,height-160))
        surface.blit(etext,(width//2+60,height-160))
        # buttons
        self.draw_buttons(surface)
        # message
        msg = self.font.render("combat",True,(255,255,255))
        surface.blit(msg,(60,height-280))