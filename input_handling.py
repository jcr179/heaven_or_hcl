import pygame, sys
from pygame.locals import *

pygame.init() 
# use before any pygame function 

DISPLAYSURF = pygame.display.set_mode((400, 300)) 
# returns pygame.Surface object for the window and sets window size in pixels

pygame.display.set_caption('Hello World!')
# sets caption text appearing as window name 

while True: # often used for main game loop: handle events, update game state, draw state to screen
    for event in pygame.event.get():
        ''' 
        any time the user does an action like pressing a key or moving the mouse,
        a pygame.event.Event object is created by the pygame library.
        The function pygame.event.get() returns a list of such events that have happened
        since the last call to pygame.event.get() in the order the events
        happened. Can return an empty list if nothing happened since last call.
        '''

        '''
        event objects have a .type that says what kind of event the object represents.
        one such event type is QUIT (a constant, imported from pygame.locals)
        '''

        if event.type == QUIT: 
            pygame.quit()
            sys.exit()

    pygame.display.update()

        

        