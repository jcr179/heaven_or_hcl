import pygame
from os import getcwd
from os.path import isdir, join
from sys import exit

global img_dir 

check_dir = join(getcwd(), "resources", "images")
if isdir(check_dir):
    img_dir = check_dir

else:
    print("Image directory ", check_dir, " does not exist.")

def initOverlay(layout="fightstick"):
    
    # load images for fightstick layout, implement switch later
    base = pygame.image.load(join(img_dir, "overlay_fs_null.png")).convert()
    buttonOn = pygame.image.load(join(img_dir, "overlay_fs_button.png")).convert()
    balltop = pygame.image.load(join(img_dir, "overlay_fs_balltop.png")).convert()

    return base, buttonOn, balltop 