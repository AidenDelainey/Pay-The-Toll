##### game setup ###3
import os
import random

WIDTH = 1024
HEIGHT = 640
FPS = 60
TILESIZE = 64

def roll_dice(sides):
    return random.randint(1, sides)

font_path = os.path.join("..", "font", "Pixel.otf")
sound_path = os.path.join("..","sound")
image_path = os.path.join("..","image")
combat_path = os.path.join(sound_path,"combat")
inventory_path = os.path.join(image_path, "inventory_img")
enemies_path = os.path.join(image_path, "enemies")
combat_img_path = os.path.join(image_path, "combat_img")