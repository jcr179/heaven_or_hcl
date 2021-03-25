import pygame

def init_screen_and_clock(surf_x_size, surf_y_size, app_name="Game"):
    global screen, display, clock
    pygame.init()
    WINDOW_SIZE = (surf_x_size, surf_y_size)
    pygame.display.set_caption(app_name)
    screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)
    clock = pygame.time.Clock()
    return (screen, clock)

def create_fonts(font_sizes_list):
    #"Creates different fonts with one list"
    fonts = []
    for size in font_sizes_list:
        fonts.append(
            pygame.font.SysFont("lucidaconsole", size))
    return fonts
 
 
def render(fnt, what, color, where):
    #"Renders the fonts as passed from display_fps"
    text_to_show = fnt.render(what, 0, pygame.Color(color))
    screen.blit(text_to_show, where)
 
 
def display_fps(fonts, pos=(0,0)):
    #"Data that will be rendered and blitted in _display"
    render(
        fonts[-2],
        what=str(int(round(clock.get_fps()))) + " fps",
        color="white",
        where=pos)