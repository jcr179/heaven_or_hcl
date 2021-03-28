import pygame

pygame.init()
pygame.joystick.init()
joystick_count = pygame.joystick.get_count()
if joystick_count:
    joystick = pygame.joystick.Joystick(0)
else:
    print("No controller detected. Exiting safely.")
    sys.exit(0)
name = joystick.get_name()
with open ('Controller name.txt', 'w') as f:
    f.write(name)