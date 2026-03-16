# combat #
import pygame
from settings import *
from settings import roll_dice
pygame.init()

select_snd = pygame.mixer.Sound(os.path.join(sound_path, "item hover.mp3"))
weapon_swing_snd = pygame.mixer.Sound(os.path.join(combat_path, "weapon swing.mp3"))
immune_hit_snd = pygame.mixer.Sound(os.path.join(combat_path, "immune hit.mp3"))
resist_hit_snd = pygame.mixer.Sound(os.path.join(combat_path, "strong hit.mp3"))
weak_hit_snd = pygame.mixer.Sound(os.path.join(combat_path, "weak hit.mp3"))
normal_hit_snd = pygame.mixer.Sound(os.path.join(combat_path, "normal hit.mp3"))
spell_cast_snd = pygame.mixer.Sound(os.path.join(combat_path, "spell cast.mp3"))
heal_spell_snd = pygame.mixer.Sound(os.path.join(combat_path, "heal spell.mp3"))

class CombatSystem:
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy
        
        self.turn = "player"
        self.finished = False
        
        self.font = pygame.font.Font(font_path, 24)
        
        self.options = ["Attack", "Spell", "Heal", "Run"]
        self.selected_option = 0
        
        self.enemy_turn_delay = 800
        self.enemt_turn_start = None
        
        self.max_heals = 3
        self.heals_used = 0
        
    ### player ### 
    
    def player_attack(self):
        base_attack = self.player.get_stat("attack")
        dice_roll = roll_dice(4)
        
        raw_damage = max(1, base_attack + dice_roll)
        resist = self.enemy.resistance.get("physical", 0)
        
        final_damage = max(0, int(raw_damage * (1 - resist) - self.enemy.defence))
        self.enemy.health -= final_damage
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
            
    def player_spell(self):
        base_attack = self.player.get_stat("spell")
        dice = roll_dice(6)
        raw = base_attack + dice
        
        resist = self.enemy.resistance.get("spell", 0)
        damage = int(raw * (1 - resist))
        
        self.enemy.health -= damage
        spell_cast_snd.play()
        
        self.turn = "enemy"
        self.enemy_turn_start = pygame.time.get_ticks()
        
    
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
        
        #self.turn = "enemy"
        #self.enemy_turn_start = pygame.time.get_ticks()
        
    def player_run(self):
        self.finished = True
            
        ### enemy ###
            
    def enemy_attack(self):
        dice = roll_dice(4)
        damage = max(1, self.enemy.attack + dice - self.player.get_stat("defence"))
            
        self.player.current_health -= damage
        self.player.current_health = max(0, self.player.current_health)
        weapon_swing_snd.play()
        self.turn = "player"
            
        ### inputs ###
        
    def handle_input(self, event):
            
        if self.turn != "player":
            return
            
        if event.type == pygame.KEYDOWN:
                
            if event.key == pygame.K_a:
                self.selected_option -= 1
                if self.selected_option < 0:
                    self.selected_option = len(self.options) - 1
                select_snd.play()
                
            if event.key == pygame.K_d:
                self.selected_option += 1
                if self.selected_option >= len(self.options):
                    self.selected_option = 0
                select_snd.play()
            
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                
                if self.selected_option == 0:
                    self.player_attack()
                
                elif self.selected_option == 1:
                    self.player_spell()
                    
                elif self.selected_option == 2:
                    self.player_heal()
                    
                elif self.selected_option == 3:
                    self.player_run()

                    
                    
    def update(self):
        if self.enemy.health <= 0:
             self.finished = True
             return
            
        if self.player.current_health <= 0:
            self.finished = True
            return
            
        if self.turn == "enemy" and not self.finished:
            now = pygame.time.get_ticks()
            
            if self.enemy_turn_start and now - self.enemy_turn_start >= self.enemy_turn_delay:
                self.enemy_attack()
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
  