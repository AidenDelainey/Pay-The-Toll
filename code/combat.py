# combat #
import pygame
from settings import *
import random

pygame.init()

# sounds #
select_snd = pygame.mixer.Sound(os.path.join(sound_path, "item hover.mp3"))
weapon_swing_snd = pygame.mixer.Sound(os.path.join(combat_path, "weapon swing.mp3"))
immune_hit_snd = pygame.mixer.Sound(os.path.join(combat_path, "immune hit.mp3"))
resist_hit_snd = pygame.mixer.Sound(os.path.join(combat_path, "strong hit.mp3"))
weak_hit_snd = pygame.mixer.Sound(os.path.join(combat_path, "weak hit.mp3"))
normal_hit_snd = pygame.mixer.Sound(os.path.join(combat_path, "normal hit.mp3"))
spell_cast_snd = pygame.mixer.Sound(os.path.join(combat_path, "spell cast.mp3"))
heal_spell_snd = pygame.mixer.Sound(os.path.join(combat_path, "heal spell.mp3"))
marker_hit_snd = pygame.mixer.Sound(os.path.join(combat_path, "marker hit.mp3"))

# images #



class CombatSystem:
    def __init__(self, player, enemies):
        self.player = player
        self.enemies = enemies
        self.all_enemies = enemies.copy()
        
        self.current_target = 0

        self.turn = "player"
        self.state = "PLAYER_MENU"
        self.finished = False

        self.font = pygame.font.Font(font_path, 24)

        self.options = ["Attack", "Spell", "Heal"]
        self.selected_option = 0

        self.enemy_turn_delay = 800
        self.enemy_turn_start = None

        self.enemy_queue = []
        self.active_enemy = None
        self.enemy_index = 0

        self.max_heals = 3
        self.heals_used = 0

        self.spell_power = 1
        self.spell_hits = 0
        self.max_spell_hits = 3

        self.bar_pos = 0
        self.bar_speed = 0
        self.target_pos = 0
        self.target_width = 0.1
        self.safe_zone = 0
        self.safe_width = 0.15

        self.result = None

    # -------------------------
    # PLAYER ACTIONS
    # -------------------------

    def get_target(self):
        if not self.enemies:
            return None
        return self.enemies[self.current_target]

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

    # -------------------------
    # ATTACK
    # -------------------------

    def start_attack_minigame(self):
        self.state = "ATTACK_MINIGAME"
        self.bar_pos = 0
        self.bar_speed = random.choice([0.014, 0.018, 0.022])
        self.target_pos = random.uniform(0.15, 0.85)
        self.target_width = 0.12

    def confirm_attack(self, missed=False):

        distance = abs(self.bar_pos - self.target_pos)
        accuracy = max(0, 1 - (distance / self.target_width))
        self.resolve_attack(accuracy, False)

    def resolve_attack(self, accuracy, missed):
        enemy = self.get_target()
        if not enemy:
            return

        base_attack = self.player.get_stat("attack")
        raw = base_attack + roll_dice(4)

        multiplier = 0.5 + (accuracy * 1.5)
        damage = int(raw * multiplier)

        resist = enemy.resistance.get("physical", 0)
        final_damage = max(0, int(damage * (1 - resist) - enemy.defence))

        enemy.health = max(0, enemy.health - final_damage)

        weapon_swing_snd.play()

        if final_damage == 0:
            immune_hit_snd.play()
        elif resist > 0:
            resist_hit_snd.play()
        elif resist < 0:
            weak_hit_snd.play()
        else:
            normal_hit_snd.play()

        self.cleanup_dead_enemies()
        if len(self.enemies) == 0:
            self.result = "win"
            self.finished = True
            return
        
        self.start_enemy_turn()

    # -------------------------
    # SPELL
    # -------------------------

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
        enemy = self.get_target()
        if not enemy:
            return

        raw = self.player.get_stat("spell") + roll_dice(6)
        damage = int(raw * self.spell_power)

        resist = enemy.resistance.get("spell", 0)
        final_damage = int(damage * (1 - resist))

        enemy.health = max(0, enemy.health - final_damage)

        spell_cast_snd.play()

        self.cleanup_dead_enemies()
        
        if len(self.enemies) == 0:
            self.result = "win"
            self.finished = True
            return
        self.start_enemy_turn()

    # -------------------------
    # ENEMY TURN
    # -------------------------

    def start_enemy_turn(self):
        self.turn = "enemy"
        self.state = "WAITING"
        self.enemy_turn_start = pygame.time.get_ticks()

        self.enemy_queue = self.enemies.copy()
        self.enemy_index = 0

    def start_dodge_minigame(self):
        if self.enemy_index >= len(self.enemy_queue):
            self.turn = "player"
            self.state = "PLAYER_MENU"
            return

        self.active_enemy = self.enemy_queue[self.enemy_index]
        self.enemy_index += 1

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
        enemy = self.active_enemy
        if not enemy:
            return

        raw = enemy.attack + roll_dice(4)
        reduction = accuracy * 0.5

        damage = int(raw * (1 - reduction) - self.player.get_stat("defence"))
        damage = max(0, damage)

        self.player.current_health = max(0, self.player.current_health - damage)

        weapon_swing_snd.play()

        self.start_dodge_minigame()

    # -------------------------
    # HELPERS
    # -------------------------

    def cleanup_dead_enemies(self):
        self.enemies = [e for e in self.enemies if e.health > 0]

        if self.current_target >= len(self.enemies):
            self.current_target = max(0, len(self.enemies) - 1)

    # -------------------------
    # INPUT
    # -------------------------

    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if self.state == "PLAYER_MENU":

            if event.key == pygame.K_a:
                self.selected_option = (self.selected_option - 1) % len(self.options)
                select_snd.play()

            elif event.key == pygame.K_d:
                self.selected_option = (self.selected_option + 1) % len(self.options)
                select_snd.play()

            elif event.key == pygame.K_q:
                self.current_target = (self.current_target - 1) % len(self.enemies)

            elif event.key == pygame.K_e:
                self.current_target = (self.current_target + 1) % len(self.enemies)

            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):

                if self.selected_option == 0:
                    self.start_attack_minigame()

                elif self.selected_option == 1:
                    self.start_spell_minigame()

                elif self.selected_option == 2:
                    self.player_heal()

                #elif self.selected_option == 3:
                    #self.player_run()

        elif self.state == "ATTACK_MINIGAME":
            if event.key == pygame.K_SPACE:
                self.confirm_attack()

        elif self.state == "DODGE_MINIGAME":
            if event.key == pygame.K_SPACE:
                self.confirm_dodge()

        elif self.state == "SPELL_MINIGAME":
            if event.key == pygame.K_SPACE:
                self.confirm_spell()

    # -------------------------
    # UPDATE
    # -------------------------

    def update(self):
        if len(self.enemies) == 0:
            self.result = "win"
            self.finished = True
            return

        if self.player.current_health <= 0:
            self.result = "lose"
            self.finished = True
            return

        if self.state in ("ATTACK_MINIGAME", "DODGE_MINIGAME", "SPELL_MINIGAME"):
            self.update_bar()

        if self.turn == "enemy":
            now = pygame.time.get_ticks()

            if self.enemy_turn_start and now - self.enemy_turn_start >= self.enemy_turn_delay:
                self.start_dodge_minigame()
                self.enemy_turn_start = None

    def update_bar(self):
        self.bar_pos += self.bar_speed

        if self.bar_pos >= 1 or self.bar_pos <= 0:
            self.bar_speed *= -1

    # -------------------------
    # DRAW (MULTI ENEMY)
    # -------------------------

    def draw(self, surface):
        width, height = surface.get_size()

        panel = pygame.Rect(0, height - 200, width, 200)
        pygame.draw.rect(surface, (120, 70, 20), panel)
        pygame.draw.rect(surface, (255, 255, 255), panel, 4)

        # player HP
        self.draw_health_bar(
            surface,
            60, height - 120,
            300, 25,
            self.player.current_health,
            self.player.max_hp
        )
        
        label = self.font.render("YOU", True, (255, 255, 255))
        surface.blit(label, (60, height - 150))
        
        if self.state == "ATTACK_MINIGAME":
            self.draw_bar(surface, self.target_pos, self.target_width)

        elif self.state == "DODGE_MINIGAME":
            self.draw_bar(surface, self.safe_zone, self.safe_width)

        elif self.state == "SPELL_MINIGAME":
            self.draw_bar(surface, self.target_pos, self.target_width)
                
        for i, enemy in enumerate(self.enemies):
            x = (width // 2 - 100) + i * 180

            self.draw_health_bar(
                surface,
                x, height - 120,
                150, 20,
                enemy.health,
                enemy.max_health
            )

            name = self.font.render(enemy.name, True, (0, 0, 0))
            surface.blit(name, (x, height - 150))

            if i == self.current_target:
                pygame.draw.rect(surface, (255, 255, 0),
                                 (x - 5, height - 125, 160, 30), 2)
                
            heal_text = self.font.render(
                f"Heals: {self.max_heals - self.heals_used}",
                True, (255, 255, 255)
            )

            surface.blit(heal_text, (width - 220, height - 50))
                
            self.draw_buttons(surface)

    def draw_health_bar(self, surface, x, y, width, height, current, maxhp):
        ratio = current / maxhp

        pygame.draw.rect(surface, (0,0,0), (x-2, y-2, width+4, height+4))
        pygame.draw.rect(surface, (120,0,0), (x, y, width, height))
        pygame.draw.rect(surface, (255,50,50), (x, y, width * ratio, height))

        hp_text = self.font.render(f"{current} / {maxhp}", True, (255,255,255))
        text_rect = hp_text.get_rect(center=(x + width//2, y + height + 15))
        surface.blit(hp_text, text_rect)

    def draw_buttons(self, surface):
        width, height = surface.get_size()

        for i, text in enumerate(self.options):
            x = 60 + i * 160
            y = height - 60

            color = (255, 255, 120) if i == self.selected_option else (160, 160, 160)

            rect = pygame.Rect(x, y, 140, 40)
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, (0, 0, 0), rect, 2)

            label = self.font.render(text, True, (0, 0, 0))
            surface.blit(label, label.get_rect(center=rect.center))
            
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
