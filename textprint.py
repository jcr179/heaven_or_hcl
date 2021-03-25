import pygame

class TextPrint(object):
    """
    This is a simple class that will help us print to the screen
    It has nothing to do with the joysticks, just outputting the
    information.
    """
    def __init__(self, x_pos=10, y_pos=10, font="lucidaconsole", size=20):
        """ Constructor """
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.x_reset_pos = self.x_pos 
        self.y_reset_pos = self.y_pos
        self.reset()
        self.font = pygame.font.SysFont(font, size)
 
    def print(self, my_screen, text_string, color=(255, 255, 255), unicode=False):
        """ Draw text onto the screen. """
        if not unicode:
            text_bitmap = self.font.render(text_string, True, color)
        
        my_screen.blit(text_bitmap, [self.x_pos, self.y_pos])
        self.y_pos += self.line_height
 
    def reset(self, newline_spacing=25):
        """ Reset text to the top of the screen. """
        self.x_pos = self.x_reset_pos
        self.y_pos = self.y_reset_pos
        self.line_height = newline_spacing
 
    def indent(self):
        """ Indent the next line of text """
        self.x_pos += 10
 
    def unindent(self):
        """ Unindent the next line of text """
        self.x_pos -= 10