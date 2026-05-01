##### game setup ###3
import os
import random

WIDTH = 1000
HEIGHT = 700
FPS = 60
TILESIZE = 64

def roll_dice(sides):
    return random.randint(1, sides)

font_path = os.path.join("..", "font", "Pixel.otf")
sound_path = os.path.join("..","sound")
combat_path = os.path.join("..","sound","combat")
image_path = os.path.join("..","image")
