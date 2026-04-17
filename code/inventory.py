import pygame
from settings import *

pygame.init()

BG_COLOR = (120, 120, 120)
PANEL_COLOR = (230, 210, 160)
BORDER_COLOR = (90, 45, 0)
SLOT_COLOR = (190, 170, 120)
HIGHLIGHT_COLOR = (200, 185, 130)
TEXT_COLOR = (20, 20, 20)

equip_item_snd = pygame.mixer.Sound(os.path.join(sound_path, "item equip.mp3"))
hover_item_snd = pygame.mixer.Sound(os.path.join(sound_path, "item hover.mp3"))

TITLE_FONT = pygame.font.Font(font_path, 28,)
UI_FONT = pygame.font.Font(font_path, 20)
ACC_FONT = pygame.font.Font(font_path, 20)

class Inventory():
    def __init__(self, player):
        self.player = player
        self.display_surface = pygame.display.get_surface()
        
        self.items = []
        self.selected_index = 0
        self.scroll_offset = 0
        self.max_visible = 8
        padding = 20
        
        self.selecting_accessory_slot = False
        self.pending_item = None
        
        screen_w = self.display_surface.get_width()
        screen_h = self.display_surface.get_height()
        
        width = int(screen_w * 0.8)
        height = int(screen_h * 0.8)
        
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        
        
        self.cover_rect = pygame.Rect(x, y, width, height)
        
        page_width = (self.cover_rect.width - padding * 3) // 2
        page_height = self.cover_rect.height - padding * 2
        
        self.left_page = pygame.Rect(
            self.cover_rect.x + padding,
            self.cover_rect.y + padding,
            page_width,
            page_height
        )
        
        self.right_page = pygame.Rect(
            self.left_page.right + padding,
            self.cover_rect.y + padding,
            page_width,
            page_height
        )


    def add_item(self, item):
        inv_quantity = 0
        if item.stackable:
            for inv_item in self.items:
                if inv_item.name == item.name:
                    inv_quantity += item.quantity
                    return
        self.items.append(item)
        
    def remove_item(self, item):
        if item in self.items:
            index_removed = self.items.index(item)
            self.items.remove(item)
            
            if self.selected_index >= len(self.items):
                self.selected_index = max(0, len(self.items) - 1)
            
    
    def use_selected(self):
        if not self.items:
            return
        item = self.items[self.selected_index]
        
        if item.type == "weapon":
            old_weapon = self.player.weapon
            self.player.weapon = item
            self.remove_item(item)
            if old_weapon:
                self.add_item(old_weapon)
            equip_item_snd.play()
            return
        if item.type == "spell":
            old_spell = self.player.spell
            self.player.spell = item
            self.remove_item(item)
            equip_item_snd.play()
            if old_spell:
                self.add_item(old_spell)
        
        if item.type == "accessory":
            self.selecting_accessory_slot = True
            self.pending_item = item
            return
                
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if self.selecting_accessory_slot:
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                    if event.key == pygame.K_1:
                        acc_slot = 0
                    elif event.key == pygame.K_2:
                        acc_slot = 1
                    elif event.key == pygame.K_3:
                        acc_slot = 2
                    self.player.equip_accessory_to_slot(self.pending_item, acc_slot, self)
                    self.selecting_accessory_slot = False
                    self.pending_item = None
                    equip_item_snd.play()
                return
            
            if event.key == pygame.K_s:
                if self.items:
                    self.selected_index = min(self.selected_index + 1, len(self.items) - 1)
                    hover_item_snd.play()
            elif event.key == pygame.K_w:
                if self.items:
                    self.selected_index = max(self.selected_index - 1, 0)
                    hover_item_snd.play()
            elif event.key == pygame.K_SPACE:
                self.use_selected()
            elif event.key == pygame.K_p:
                self.player.current_health = self.player.max_hp
    # Scroll logic
            if self.selected_index >= self.scroll_offset + self.max_visible:
                self.scroll_offset += 1
            elif self.selected_index < self.scroll_offset:
                self.scroll_offset -= 1                
                    
    def draw(self):
        overlay = pygame.Surface(self.display_surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.display_surface.blit(overlay, (0, 0))
        self.draw_book()
        self.draw_equipment()
        self.draw_inventory()
        self.draw_description()

    def draw_description(self):
        if not self.items:
            return

        item = self.items[self.selected_index]

        page = self.right_page
        padding = 20

        # Description box at bottom of right page
        desc_rect = pygame.Rect(
            page.x + padding,
            page.bottom - 100,
            page.width - padding * 2,
            80
        )

        pygame.draw.rect(self.display_surface,
                         SLOT_COLOR, desc_rect, border_radius=6)
        pygame.draw.rect(self.display_surface,
                         BORDER_COLOR, desc_rect, 2, border_radius=6)

        # Wrap text if too long
        words = item.description.split(" ")
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            if UI_FONT.size(test_line)[0] < desc_rect.width - 10:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "

        lines.append(current_line)

        # Render lines
        for i, line in enumerate(lines[:3]):  # limit lines so it stays inside page
            text = UI_FONT.render(line.strip(), True, TEXT_COLOR)
            self.display_surface.blit(
                text,
                (desc_rect.x + 5, desc_rect.y + 5 + i * 22)
            )

    def draw_book(self):
        pygame.draw.rect(self.display_surface, (70, 35, 10),
                         self.cover_rect, border_radius=8)

        pygame.draw.rect(self.display_surface, PANEL_COLOR,
                         self.left_page, border_radius=6)

        pygame.draw.rect(self.display_surface, PANEL_COLOR,
                         self.right_page, border_radius=6)

        pygame.draw.line(self.display_surface, (120, 90, 50),
                         (self.right_page.x, self.left_page.y),
                         (self.right_page.x, self.left_page.bottom), 4)

        self.display_surface.blit(
            TITLE_FONT.render("Equipment", True, TEXT_COLOR),
            (self.left_page.x + 20, self.left_page.y + 10))

        self.display_surface.blit(
            TITLE_FONT.render("Inventory", True, TEXT_COLOR),
            (self.right_page.x + 20, self.right_page.y + 10))


    def draw_equipment(self):
        page = self.left_page
        slot_size = int(self.left_page.width * 0.25)
        spacing = 20

        total_width = slot_size * 2 + spacing
        start_x = page.x + (page.width - total_width) // 2
        start_y = page.y + 60

        # ---------- Weapon Slot ----------
        weapon_rect = pygame.Rect(start_x, start_y, slot_size, slot_size)
        self.draw_slot(weapon_rect, self.player.weapon)

        # ---------- Spell Slot ----------
        spell_rect = pygame.Rect(start_x + slot_size + spacing, start_y, slot_size, slot_size)
        self.draw_slot(spell_rect, self.player.spell)

        # ---------- Accessories ----------
        acc_y = start_y + slot_size + 40
        total_acc_width = slot_size * 3 + spacing * 2
        acc_start_x = page.x + (page.width - total_acc_width) // 2

        for i in range(3):
            rect = pygame.Rect(acc_start_x + i * (slot_size + spacing), acc_y, slot_size, slot_size)
            label = "A" if self.player.accessories[i] else ""
            self.draw_slot(rect, self.player.accessories[i])

        # ---------- Health Bar ----------
        stats_y = acc_y + slot_size + 40
        bar_x = page.x + 20
        bar_y = stats_y - 25
        bar_width = page.width - 40
        bar_height = 18

        # Use the max_hp property from player
        ratio = self.player.current_health / self.player.max_hp
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        hp_rect = pygame.Rect(bar_x, bar_y, bar_width * ratio, bar_height)

        pygame.draw.rect(self.display_surface, (100, 100, 100), bg_rect)
        pygame.draw.rect(self.display_surface, (200, 0, 0), hp_rect)
        pygame.draw.rect(self.display_surface, BORDER_COLOR, bg_rect, 2)

        # HP text
        hp_text_surface = UI_FONT.render(f"{self.player.current_health}/{self.player.max_hp}", True, TEXT_COLOR)
        self.display_surface.blit(
            hp_text_surface,
            (bar_x + bar_width // 2 - hp_text_surface.get_width() // 2, bar_y - 3)
        )

        # ---------- Stats Display ----------
        stats = [
            ("ATK", "attack"),
            ("DEF", "defence"),
            ("SPL", "spell"),
            ("HEL", "healing")
        ]

        for i, (label, stat) in enumerate(stats):
            text_surface = UI_FONT.render(f"{label}: {self.player.get_stat(stat)}", True, TEXT_COLOR)
            self.display_surface.blit(text_surface, (page.x + 20, stats_y + i * 30))

        # ---------- Accessory slot selection ----------
        if self.selecting_accessory_slot:
            prompt_surface = ACC_FONT.render("Press 1 / 2 / 3 to choose slot", True, TEXT_COLOR)
            self.display_surface.blit(prompt_surface, (page.x + 40, page.bottom - 360))

    def draw_inventory(self):
        page = self.right_page
        padding = 20
        start_x = page.x + padding
        start_y = page.y + 60
        row_height = 40
        row_width = page.width - padding * 2

        visible = self.items[self.scroll_offset:
                             self.scroll_offset + self.max_visible]

        for i, item in enumerate(visible):
            actual_index = i + self.scroll_offset
            y = start_y + i * row_height

            if y + row_height > page.bottom - 110:
                break

            rect = pygame.Rect(start_x, y, row_width, row_height - 5)

            color = (HIGHLIGHT_COLOR if
                     actual_index == self.selected_index
                     else SLOT_COLOR)

            pygame.draw.rect(self.display_surface,
                             color, rect, border_radius=6)
            
            if item.image:
                icon_size = row_height - 8
                img = pygame.transform.scale(item.image, (icon_size,icon_size))
                self.display_surface.blit(img, (rect.x + 5, rect.y + 6))


            # Item name
            text = UI_FONT.render(item.name, True, TEXT_COLOR)
            self.display_surface.blit(text, (rect.x + + icon_size + 10, rect.y + (row_height - text.get_height())//2))

            # Quantity
            if item.quantity > 1:
                qty_text = UI_FONT.render(str(item.quantity),
                                          True, TEXT_COLOR)
                self.display_surface.blit(
                    qty_text,
                    (rect.right - 10 - qty_text.get_width(),
                     rect.y + 8))
        

    # =========================
    # HELPER
    # =========================
    def draw_slot(self, rect, item=None, label=""):
        pygame.draw.rect(self.display_surface,
                         SLOT_COLOR, rect, border_radius=10)
        pygame.draw.rect(self.display_surface,
                         BORDER_COLOR, rect, 3, border_radius=10)
        if item and hasattr(item, "image") and item.image:
            img = pygame.transform.scale(item.image, (rect.width - 10, rect.height - 10))
            self.display_surface.blit(
                img, (rect.x + 5, rect.y + 5))

        elif label:
            text = UI_FONT.render(label, True, TEXT_COLOR)
            self.display_surface.blit(
                text,
                (rect.centerx - text.get_width() // 2,
                 rect.centery - text.get_height() // 2))