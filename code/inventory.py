import pygame
import os
from settings import *

pygame.init()

TEXT_COLOR = (20, 20, 20)

def load_sound(path):
    try:
        return pygame.mixer.Sound(path)
    except:
        return None

equip_item_snd = load_sound(os.path.join(sound_path, "item equip.mp3"))
hover_item_snd = load_sound(os.path.join(sound_path, "item hover.mp3"))

inventory_bg = pygame.image.load(os.path.join(inventory_path, "inventory_backround.png")).convert_alpha()
hp_overlay = pygame.image.load(os.path.join(inventory_path, "inventory hp overlay.png")).convert_alpha()

inv_slot_img = pygame.image.load(os.path.join(inventory_path, "inventory list unselected.png")).convert_alpha()
inv_slot_selected_img = pygame.image.load(os.path.join(inventory_path, "inventory list selected.png")).convert_alpha()

selector_img = pygame.image.load(os.path.join(inventory_path, "inventory_selector.png")).convert_alpha()

UI_FONT = pygame.font.Font(font_path, 20)


class Inventory():
    def __init__(self, player):
        self.player = player
        self.display_surface = pygame.display.get_surface()

        self.items = []
        self.selected_index = 0
        self.scroll_offset = 0
        self.max_visible = 5

        self.hovered_index = None
        self.prev_hovered_index = None
        self.hovered_acc_slot = None

        self.selecting_accessory_slot = False
        self.pending_item = None

        screen_w = self.display_surface.get_width()
        screen_h = self.display_surface.get_height()

        width = int(screen_w * 0.95)
        height = int(screen_h * 0.95)

        x = (screen_w - width) // 2
        y = (screen_h - height) // 2

        self.cover_rect = pygame.Rect(x, y, width, height)

        img_w, img_h = inventory_bg.get_size()
        self.scale = min(self.cover_rect.width / img_w, self.cover_rect.height / img_h)

        new_size = (int(img_w * self.scale), int(img_h * self.scale))
        self.bg_image = pygame.transform.scale(inventory_bg, new_size)
        self.bg_rect = self.bg_image.get_rect(center=self.cover_rect.center)

        sw, sh = inv_slot_img.get_size()
        self.inv_slot_img = pygame.transform.scale(inv_slot_img, (int(sw*self.scale), int(sh*self.scale)))
        self.inv_slot_selected_img = pygame.transform.scale(inv_slot_selected_img, (int(sw*self.scale), int(sh*self.scale)))

        sel_w, sel_h = selector_img.get_size()
        self.selector_img = pygame.transform.scale(selector_img, (int(sel_w*self.scale), int(sel_h*self.scale)))

        bx, by = self.bg_rect.topleft
        bw, bh = self.bg_rect.size

        self.weapon_pos = (bx + bw * 0.20, by + bh * 0.25)
        self.spell_pos = (bx + bw * 0.36, by + bh * 0.25)

        self.accessory_positions = [
            (bx + bw * 0.135, by + bh * 0.41),
            (bx + bw * 0.275, by + bh * 0.41),
            (bx + bw * 0.415, by + bh * 0.41),
        ]

        self.hp_bar_rect = pygame.Rect(
            bx + bw * 0.075,
            by + bh * 0.48,
            bw * 0.40,
            bh * 0.05
        )

        self.hp_overlay_img = pygame.transform.scale(
            hp_overlay,
            (int(self.hp_bar_rect.width), int(self.hp_bar_rect.height))
        )

        self.desc_rect = pygame.Rect(
            bx + bw * 0.55,
            by + bh * 0.59,
            bw * 0.35,
            bh * 0.20
        )

        padding = 40
        page_width = (self.bg_rect.width - padding * 3) // 2
        page_height = self.bg_rect.height - padding * 2

        self.right_page = pygame.Rect(
            self.bg_rect.x + padding * 2 + page_width,
            self.bg_rect.y + padding,
            page_width,
            page_height
        )

    # =========================
    # HOVER DETECTION
    # =========================
    def update_hovered_inventory(self):
        mouse = pygame.mouse.get_pos()
        self.hovered_index = None

        slot_w, slot_h = self.inv_slot_img.get_size()
        spacing = int(slot_h * 0.15)

        start_y = self.right_page.y + int(self.right_page.height * 0.15)
        start_x = self.right_page.x + (self.right_page.width - slot_w) // 2

        for i in range(self.max_visible):
            idx = i + self.scroll_offset
            if idx >= len(self.items):
                break

            y = start_y + i * (slot_h + spacing)
            rect = pygame.Rect(start_x, y, slot_w, slot_h)

            if rect.collidepoint(mouse):
                self.hovered_index = idx
                break

        # hover sound
        if self.hovered_index != self.prev_hovered_index:
            if hover_item_snd:
                hover_item_snd.play()
            self.prev_hovered_index = self.hovered_index

    def update_hovered_accessory(self):
        mouse = pygame.mouse.get_pos()
        self.hovered_acc_slot = None

        for i, pos in enumerate(self.accessory_positions):

            rect = self.selector_img.get_rect(center=(int(pos[0]), int(pos[1])))

            if rect.collidepoint(mouse):
                self.hovered_acc_slot = i
                break

    # =========================
    # INPUT
    # =========================
    def handle_input(self, event):

        if event.type == pygame.MOUSEMOTION:
            self.update_hovered_inventory()

        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset -= event.y
            self.scroll_offset = max(0, min(self.scroll_offset, max(0, len(self.items)-self.max_visible)))

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            if self.selecting_accessory_slot:
                self.update_hovered_accessory()

                if self.hovered_acc_slot is not None:
                    self.player.equip_accessory_to_slot(self.pending_item, self.hovered_acc_slot, self)
                    self.selecting_accessory_slot = False
                    self.pending_item = None

                    if equip_item_snd:
                        equip_item_snd.play()

                return

            if self.hovered_index is not None:
                self.selected_index = self.hovered_index
                self.use_selected()

    # =========================
    # ITEM LOGIC
    # =========================
    def add_item(self, item):
        if item.stackable:
            for inv_item in self.items:
                if inv_item.name == item.name:
                    inv_item.quantity += item.quantity
                    return
        self.items.append(item)

    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)
            self.selected_index = max(0, min(self.selected_index, len(self.items)-1))

    def swap_item(self, attr, item):
        old = getattr(self.player, attr)
        setattr(self.player, attr, item)
        self.remove_item(item)

        if old:
            self.add_item(old)

        if equip_item_snd:
            equip_item_snd.play()

    def use_selected(self):
        if not self.items:
            return

        item = self.items[self.selected_index]

        if item.type == "weapon":
            self.swap_item("weapon", item)
        elif item.type == "spell":
            self.swap_item("spell", item)
        elif item.type == "accessory":
            self.selecting_accessory_slot = True
            self.pending_item = item

    # =========================
    # DRAW
    # =========================
    def draw(self):
        overlay = pygame.Surface(self.display_surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0,0,0,180))
        self.display_surface.blit(overlay,(0,0))

        self.display_surface.blit(self.bg_image, self.bg_rect.topleft)

        self.draw_equipment()
        self.draw_inventory()
        self.draw_description()
        self.draw_health_bar()
        self.draw_stats()

    def draw_inventory(self):

        slot_w, slot_h = self.inv_slot_img.get_size()
        spacing = int(slot_h * 0.15)

        start_y = self.right_page.y + int(self.right_page.height * 0.15)
        start_x = self.right_page.x + (self.right_page.width - slot_w) // 2

        for i in range(self.max_visible):
            idx = i + self.scroll_offset
            if idx >= len(self.items):
                break

            y = start_y + i * (slot_h + spacing)

            is_hovered = idx == self.hovered_index

            img = self.inv_slot_selected_img if is_hovered else self.inv_slot_img

            self.display_surface.blit(img, (start_x, y))

            item = self.items[idx]

            if item.image:
                size = max(1, slot_h - 10)
                icon = pygame.transform.scale(item.image, (size, size))
                self.display_surface.blit(icon, (start_x+8, y + (slot_h-size)//2))
                text_x = start_x + size + 16
            else:
                text_x = start_x + 8

            text = UI_FONT.render(item.name, True, TEXT_COLOR)
            self.display_surface.blit(text, (text_x, y + (slot_h - text.get_height())//2))

    def draw_equipment(self):

        def draw_item(pos, item):
            if item and getattr(item, "image", None):
                size = int(self.bg_rect.width * 0.13)
                img = pygame.transform.scale(item.image, (size, size))
                rect = img.get_rect(center=(int(pos[0]), int(pos[1])))
                self.display_surface.blit(img, rect)

        draw_item(self.weapon_pos, self.player.weapon)
        draw_item(self.spell_pos, self.player.spell)

        for i, pos in enumerate(self.accessory_positions):
            item = self.player.accessories[i] if i < len(self.player.accessories) else None
            draw_item(pos, item)

        if self.selecting_accessory_slot:
            self.update_hovered_accessory()

            if self.hovered_acc_slot is not None:
                pos = self.accessory_positions[self.hovered_acc_slot]

                sel_rect = self.selector_img.get_rect(center=(
                    int(pos[0]),
                    int(pos[1])
                ))

                self.display_surface.blit(self.selector_img, sel_rect)
                
    def draw_health_bar(self):

        # -------------------------
        # SAFETY + RATIO
        # -------------------------
        if self.player.max_hp <= 0:
            return

        ratio = self.player.current_health / self.player.max_hp
        ratio = max(0, min(1, ratio))

        # -------------------------
        # POSITION / SIZE
        # -------------------------
        x = self.hp_bar_rect.x
        y = self.hp_bar_rect.y
        w = self.hp_bar_rect.width
        h = self.hp_bar_rect.height

        bg_rect = pygame.Rect(x, y, w, h)

        # -------------------------
        # BACKGROUND SLOT (EMPTY BAR)
        # -------------------------
        pygame.draw.rect(
            self.display_surface,
            (60, 60, 60),
            bg_rect,
            border_radius=4
        )

        # -------------------------
        # FILL (CURRENT HP)
        # -------------------------
        fill_rect = pygame.Rect(
            x,
            y,
            int(w * ratio),
            h
        )

        pygame.draw.rect(
            self.display_surface,
            (200, 0, 0),
            fill_rect,
            border_radius=4
        )

        # -------------------------
        # OVERLAY 
        # -------------------------
        if self.hp_overlay_img:
            self.display_surface.blit(self.hp_overlay_img, (x, y))

        # -------------------------
        # HP TEXT
        # -------------------------
        hp_text_surface = UI_FONT.render(
            f"{self.player.current_health}/{self.player.max_hp}",
            True,
            TEXT_COLOR
        )

        self.display_surface.blit(
            hp_text_surface,
            (
                x + w // 2 - hp_text_surface.get_width() // 2,
                y - 3
            )
        )

    def draw_stats(self):

        stats = [
            ("ATK", "attack"),
            ("DEF", "defence"),
            ("SPL", "spell"),
            ("HEL", "healing")
        ]

        # anchor directly under HP bar (stable + UI-safe)
        stats_x = self.hp_bar_rect.x
        stats_y = self.hp_bar_rect.y + self.hp_bar_rect.height + 8

        line_height = UI_FONT.get_height()

        for i, (label, stat) in enumerate(stats):

            value = self.player.get_stat(stat)

            text_surface = UI_FONT.render(
                f"{label}: {value}",
                True,
                TEXT_COLOR
            )

            self.display_surface.blit(
                text_surface,
                (stats_x + 5, stats_y + i * line_height)
            )

    def draw_description(self):
        if self.hovered_index is None:
            return

        if self.hovered_index < 0 or self.hovered_index >= len(self.items):
            return

        item = self.items[self.hovered_index]
        if not item or not item.description:
            return

        words = item.description.split(' ')
        lines = []
        current_line = ""

        max_width = self.desc_rect.width
        max_height = self.desc_rect.height

        line_height = UI_FONT.get_height()
        max_lines = max_height // line_height

        for word in words:
            test_line = current_line + word + " "
            test_surface = UI_FONT.render(test_line, True, TEXT_COLOR)

            if test_surface.get_width() <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "

        if current_line:
            lines.append(current_line)

        lines = lines[:max_lines]

        old_clip = self.display_surface.get_clip()
        self.display_surface.set_clip(self.desc_rect)

        y_offset = 0
        for line in lines:
            text = UI_FONT.render(line, True, TEXT_COLOR)
            self.display_surface.blit(
                text,
                (self.desc_rect.x + 8, self.desc_rect.y + 5 + y_offset)
            )
            y_offset += line_height

        # restore
        self.display_surface.set_clip(old_clip)
