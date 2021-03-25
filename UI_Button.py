import pygame

class UI_Button():
    def __init__(self, x_pos, y_pos, w, h,  off_color, on_color, text="", font="lucidaconsole", textsize=14):
        self.off_color = off_color
        self.on_color = on_color 
        self.x_pos = x_pos 
        self.y_pos = y_pos
        self.width = w 
        self.height = h
        self.text = text 
        self.font = font 
        self.textsize = textsize
        self.toggle = False
        self.rect = None

    def draw(self, surface):

        if self.toggle:
            self.rect = pygame.draw.rect(surface, self.on_color, pygame.Rect(self.x_pos, self.y_pos, self.width, self.height), 0)

        else:
            self.rect = pygame.draw.rect(surface, self.off_color, pygame.Rect(self.x_pos, self.y_pos, self.width, self.height), 0)

        if self.text != '':
            font = pygame.font.SysFont(self.font, self.textsize)
            text_to_blit = font.render(self.text, 1, (0,0,0))
            surface.blit(text_to_blit, (self.x_pos + (self.width/2 - text_to_blit.get_width()/2), self.y_pos + (self.height/2 - text_to_blit.get_height()/2)))