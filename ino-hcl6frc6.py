import pygame
from pygame.locals import *
from textprint import TextPrint
from init_and_fps import *
import overlay
from math import floor 
import os
from move_detection import fsm_hcl, tick_hcl, frc_frame1, frc_frame2
from UI_Button import UI_Button
import sys 
import time 
from config_read import get_mapping_from_file

from ctypes import windll


# Meta
version = "v0.1"

SetWindowPos = windll.user32.SetWindowPos

NOSIZE = 1
NOMOVE = 2
TOPMOST = -1
NOT_TOPMOST = -2

def alwaysOnTop(yesOrNo):
    zorder = (NOT_TOPMOST, TOPMOST)[yesOrNo] # choose a flag according to bool 0 or 1
    hwnd = pygame.display.get_wm_info()['window'] # handle to the window
    SetWindowPos(hwnd, zorder, 0, 0, 0, 0, NOMOVE|NOSIZE)

pygame.init()

alwaysOnTop(1)

"""
Constants
"""
surf_x_size = 600
surf_y_size = 320
num_inputs = 9 # Xbox 360 controller : direction, a,b,x,y,lt,rt,lb,rb

xb_button_map = {0: "A", 1: "B", 2: "X", 3: "Y", 4: "LB", 5: "RB", 6: "Back", 7: "Start", 8: "L3", 9: "R3"}
xb_valid_button_nums = set([0, 1, 2, 3, 4, 5, 6])
xb_axis_map = {-0.996: "RT", 0.996: "LT"}
xb_dir_map = {(0, 0): 5, (1, 0): 6, (0, -1): 2, (-1, 0): 4, (0, 1): 8, (1, -1): 3, (-1, -1): 1, (-1, 1): 7, (1, 1): 9}
xb_held_axes = {"LT": False, "RT": False}
xb_axis_released = ""

"""
ps_button_map = {0: "Square", 1: "Cross", 2: "Circle", 3: "Triangle", 4: "L1", 5: "R1", 6: "L2", 7: "R2", 8: "Back", 9: "Start", 
    10: "L3", 11: "R3"}
ps_valid_button_nums = set([0, 1, 2, 3, 4, 5, 6, 7, 8])
ps_axis_map = {-0.996: "RT", 0.996: "LT"}
ps_dir_map = {(0, 0): 5, (1, 0): 6, (0, -1): 2, (-1, 0): 4, (0, 1): 8, (1, -1): 3, (-1, -1): 1, (-1, 1): 7, (1, 1): 9}
ps_held_axes = {"LT": False, "RT": False}
ps_axis_released = ""
"""

# LT+RT not supported; this gives same reading as no triggers pressed
xb_held_buttons = {}
for val in xb_button_map.values():
    xb_held_buttons[val] = -1
for val in xb_axis_map.values():
    xb_held_buttons[val] = -1

xb_held_buttons_frames = {}
for val in xb_button_map.values():
    xb_held_buttons_frames[val] = 0
for val in xb_axis_map.values():
    xb_held_buttons_frames[val] = 0

app_name = "Heaven or HCL"
screen, clock = init_screen_and_clock(surf_x_size, surf_y_size, app_name)
fonts = create_fonts([32, 16, 14, 8])
fps = 60 # include config setting for 58-62 fps?
app_icon = pygame.image.load('icon2.png')
pygame.display.set_icon(app_icon)


dt = clock.tick(fps)

run = True 

# UI Buttons
ui_btn_help = UI_Button(550, 10, 40, 20, off_color=(40, 200, 40), on_color=(40, 200, 40), text="HELP")
ui_btn_close_help = UI_Button(465, 270, 90, 20, off_color=(200, 40, 40), on_color=(200, 40, 40), text="CLOSE HELP")
ui_btn_sfx = UI_Button(510, 10, 30, 20, off_color=(128, 128, 128), on_color=(136, 248, 224), text="SFX")
ui_btn_hitstop = UI_Button(400, 10, 100, 20, off_color=(136, 248, 224), on_color=(136, 248, 224), text="HITSTOP: Raw")
ui_btn_config = UI_Button(290, 10, 100, 20, off_color=(136, 248, 224), on_color=(136, 248, 224), text="LOAD CONFIG")
ui_btn_side_switch = UI_Button(180, 10, 100, 20, off_color=(136, 248, 224), on_color=(136, 248, 224), text="SIDE SWITCH")

display_help_window = False 
#help_msg = "hello\nyep"
ui_win_help_border = UI_Button(30, 25, 540, 275, off_color=(40, 200, 40), on_color=(40, 200, 40))
ui_win_help = UI_Button(35, 30, 530, 265, off_color=(54, 57, 62), on_color=(54, 57, 62))

hitstop_changed = 0 
config_changed = 0

hitstop_frames = [0, 19, 22]
hitstop_vals = len(hitstop_frames)
hitstop_idx = 0
hitstop_dict = {
    0: "Raw",
    1: "5K",
    2: "2S"
}
hitstop = hitstop_frames[hitstop_idx]

def change_hitstop(btn):
    global hitstop_idx
    global hitstop
    hitstop_idx = (hitstop_idx + 1) % hitstop_vals
    hitstop = hitstop_frames[hitstop_idx]
    btn.text="HITSTOP: " + str(hitstop_dict[hitstop_idx])

capture_triggers_dict = {
        0: "hcl",
        1: "k",
        2: "s"
    }

hitstop_delay = 0 # Increment this with each frame as a counter to see if you've waited long enough for hitstop

# SFX
pygame.mixer.init()
pygame.mixer.music.load('hcl-6frc6.ogg') # inaudible when GG window is focused
#sfx_guide = pygame.mixer.Sound('hcl-6frc6.ogg')

# Joystick
pygame.joystick.init()

# Get ready to print text and initialize start position
x_margin=10
y_margin=10
textPrint = TextPrint(x_pos=x_margin, y_pos=10)
textPrintStates = TextPrint(x_pos=x_margin, y_pos=400)
textPrintEval = TextPrint(x_pos=x_margin, y_pos=200)
textPrintTips = TextPrint(x_pos=135, y_pos=100, font="tahoma", size=14)
textPrintHelp = TextPrint(x_pos=38, y_pos=35, font="lucidaconsole", size=12)

buttonPressed = False 
buttonReleased = False


debug = False


# Interface graphics 
ino_x_scale = 78
ino_y_scale = 140
ino_x_pos = 20
ino_y_pos = 40
img_ino_p1 = pygame.transform.scale(pygame.image.load('ino_p1.png'), (ino_x_scale, ino_y_scale)).convert()
img_ino_p2 = pygame.transform.scale(pygame.image.load('ino_p2.png'), (ino_x_scale, ino_y_scale)).convert()
first_ino_drawn = False

ino_success_x_scale = 78 #168
ino_success_y_scale = 140 #240
ino_success_x_pos = 20
ino_success_y_pos = 40
img_ino_success_p1 = pygame.transform.scale(pygame.image.load('ino_success_p1.png'), (ino_success_x_scale, ino_success_y_scale)).convert()
img_ino_success_p2 = pygame.transform.scale(pygame.image.load('ino_success_p2.png'), (ino_success_x_scale, ino_success_y_scale)).convert()

frame_counter_x_pos = 215
frame_counter_y_pos = 186
img_frame_counter = pygame.image.load('frame_counter.png').convert()
frame_counter_drawn = False

speech_x_pos = 110
speech_y_pos = 50
speech_x_scale = 176
speech_y_scale = 120
img_speech = pygame.transform.scale(pygame.image.load('speech-bubble.png'), (speech_x_scale, speech_y_scale)).convert()
first_attempt = True

kimochi_x_pos = 145
kimochi_y_pos = 95
kimochi_x_scale = 117
kimochi_y_scale = 67
img_kimochi = pygame.transform.scale(pygame.image.load('kimochi.png'), (kimochi_x_scale, kimochi_y_scale)).convert()

# Default arcade layout for now.
gg_button_map = {
    'X' : 'k',
    'A' : 'p',
    'Y' : 's',
    'RB' : 'h',
    'RT' : 'd',
    'Back' : 'select'
}
gg_button_map = get_mapping_from_file('config.txt')

overlay_x_offset = 0
overlay_y_offset = -20
overlay_x_pos = 300 + overlay_x_offset
overlay_y_pos = 50 + overlay_y_offset
overlay_base, overlay_btn, overlay_balltop = overlay.initOverlay()
overlay_rotate_deg = 0.0
overlay_scale_factor = 0.5
overlay_base = pygame.transform.rotozoom(overlay_base, overlay_rotate_deg, overlay_scale_factor).convert()
overlay_btn = pygame.transform.rotozoom(overlay_btn, overlay_rotate_deg, overlay_scale_factor).convert()
overlay_balltop = pygame.transform.rotozoom(overlay_balltop, overlay_rotate_deg, overlay_scale_factor).convert()

overlay_map = {
    0: [176 + overlay_x_offset/overlay_scale_factor, 175 + overlay_y_offset/overlay_scale_factor],      # A
    1: [256 + overlay_x_offset/overlay_scale_factor, 145 + overlay_y_offset/overlay_scale_factor],      # B
    2: [193 + overlay_x_offset/overlay_scale_factor, 87 + overlay_y_offset/overlay_scale_factor],       # X
    3: [271 + overlay_x_offset/overlay_scale_factor, 52 + overlay_y_offset/overlay_scale_factor],       # Y
    4: [445 + overlay_x_offset/overlay_scale_factor, 52 + overlay_y_offset/overlay_scale_factor],       # LB
    5: [359 + overlay_x_offset/overlay_scale_factor, 52 + overlay_y_offset/overlay_scale_factor],       # RB
    0.996: [428 + overlay_x_offset/overlay_scale_factor, 146 + overlay_y_offset/overlay_scale_factor],  # LT
    -0.996: [342 + overlay_x_offset/overlay_scale_factor, 145 + overlay_y_offset/overlay_scale_factor], # RT
    (0,0): [35 + overlay_x_offset/overlay_scale_factor, 109 + overlay_y_offset/overlay_scale_factor],   # neutral
    (0,1): [35 + overlay_x_offset/overlay_scale_factor, 84 + overlay_y_offset/overlay_scale_factor],    # up
    (0,-1): [35 + overlay_x_offset/overlay_scale_factor, 134 + overlay_y_offset/overlay_scale_factor],  # down 
    (1,0): [63 + overlay_x_offset/overlay_scale_factor, 109 + overlay_y_offset/overlay_scale_factor],   # forward 
    (-1,0): [7 + overlay_x_offset/overlay_scale_factor, 109 + overlay_y_offset/overlay_scale_factor],   # back
    (1,1): [63 + overlay_x_offset/overlay_scale_factor, 84 + overlay_y_offset/overlay_scale_factor],   # up forward
    (-1,-1): [7 + overlay_x_offset/overlay_scale_factor, 134 + overlay_y_offset/overlay_scale_factor],   # down back
    (-1,1): [7 + overlay_x_offset/overlay_scale_factor, 84 + overlay_y_offset/overlay_scale_factor],   # up back 
    (1,-1): [63 + overlay_x_offset/overlay_scale_factor, 134 + overlay_y_offset/overlay_scale_factor]    # down forward
}
for key, val in overlay_map.items():
    overlay_map[key] = (val[0]*overlay_scale_factor, val[1]*overlay_scale_factor)


prevDir = 5 # direction stick pointed last in numpad notation


# Circular input buffer
# Every frame, increment buf_ptr and add list of whatever inputs were read
# At end of buffer, reset buf_ptr to 0 and begin to overwrite
buf_size = 10
buf_ptr = 0
buffer = ['.']*buf_size

# Handling frames after doing HCL for measuring on a timeline (recv ~= recovery)
post_hcl_frames = 30 # hcl startup + active + recovery frames = 42 but will leave at 30 now because any input past that is irrelevant to hcl 6frc6
post_hcl_buf_ptr = 0
post_hcl_buffer = ['.']*(post_hcl_frames) # +1 so index n corresponds with frame n of hcl
in_hcl = False # flag for if you're in an HCL or not
post_hcl_frame_num = 0
prev_max_post_hcl_state = 0
prev_post_hcl_buffer = ['.']*(post_hcl_frames) # to let last attempt's results persist on display


# States for tracking hcl input and after hcl
fsm_hcl_state = 0
post_hcl_state = 0
prev_fsm_hcl_states = ['.']*buf_size


# evaluation
frc_success = False
frc_frame_attempt = 0
dash_gap = 999
second_6_gap = 999


# side switching
side = 'p1'
side_prev = 'p1'
side_switch_btn_pressed = False


"""
In this game, the frames of a move begin the frame after it's executed.
So if you complete an input for a move on frame M, frame 1 of that move is on frame M+1. If it's got 4 frames of startup, it hits
the opponent on frame M+4.

So once the complete input for HCL is found on frame N, its FRC window is frame N+16 and N+17.

However, actually implementing this causes more errors in timing detection in the program than if we said the FRC window was frame N+15 and N+16,
so we can leave it as it is for now.

This is the best we can do in pygame as its clock is based on millisecond accuracy. 
"""

while run:

    capture_trigger = capture_triggers_dict[hitstop_idx]
    
    for event in pygame.event.get():
         
        if event.type == QUIT: 
            run = False

        if event.type == pygame.JOYBUTTONDOWN:
            print("Joystick button pressed:", event.button)
            xb_held_buttons[xb_button_map[event.button]] = 0

        elif event.type == pygame.JOYBUTTONUP:
            print("Joystick button released:", event.button)
            xb_held_buttons_frames[xb_button_map[event.button]] = xb_held_buttons[xb_button_map[event.button]]
            xb_held_buttons[xb_button_map[event.button]] = -1

        elif event.type == pygame.JOYAXISMOTION:
            axisValue = round(event.value, 3)
            if event.axis == 2 and axisValue == -0.996:
                print("Joystick button pressed: RT")
                xb_held_axes["RT"] = True
                xb_held_buttons[xb_axis_map[axisValue]] = 0
            elif event.axis == 2 and axisValue == 0.0 and xb_held_axes["RT"]:
                print("Joystick button released: RT")
                xb_held_axes["RT"] = False
                xb_axis_released = "RT"
                xb_held_buttons_frames[xb_axis_released] = xb_held_buttons[xb_axis_map[-0.996]]
                xb_held_buttons[xb_axis_map[-0.996]] = -1
            if event.axis == 2 and axisValue == 0.996:
                print("Joystick button pressed: LT")
                xb_held_axes["LT"] = True 
                xb_held_buttons[xb_axis_map[axisValue]] = 0
            elif event.axis == 2 and axisValue == 0.0 and xb_held_axes["LT"]:
                print("Joystick button released: LT")
                xb_held_axes["LT"] = False 
                xb_axis_released = "LT"
                xb_held_buttons_frames[xb_axis_released] = xb_held_buttons[xb_axis_map[0.996]]
                xb_held_buttons[xb_axis_map[0.996]] = -1

        elif event.type == pygame.JOYHATMOTION:
            print("Direction ", xb_dir_map[event.value])
    
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            if ui_btn_sfx.rect.collidepoint(mouse_pos):
                ui_btn_sfx.toggle = not ui_btn_sfx.toggle
                if ui_btn_sfx.toggle:
                    pygame.mixer.music.play(-1)
                else:
                    if pygame.mixer.music.get_busy(): 
                        pygame.mixer.music.stop()

            elif ui_btn_hitstop.rect.collidepoint(mouse_pos):
                change_hitstop(ui_btn_hitstop)
                hitstop_changed = 1

            elif ui_btn_config.rect.collidepoint(mouse_pos):
                gg_button_map = get_mapping_from_file('config.txt')
                config_changed = 1

            elif ui_btn_help.rect.collidepoint(mouse_pos):
                display_help_window = True

            elif ui_btn_close_help.rect and ui_btn_close_help.rect.collidepoint(mouse_pos):
                display_help_window = False

            elif ui_btn_side_switch.rect.collidepoint(mouse_pos):
                side_prev = side 
                if side == 'p1': side = 'p2'
                else: side = 'p1'
                
                side_switch_btn_pressed = True


    # Handle graphics each tick
    textPrint.reset()
    textPrintStates.reset()
    textPrintEval.reset()
    textPrintTips.reset(15)
    screen.fill((0, 0, 0)) # put before drawing

    
    screen.blit(overlay_base, [overlay_x_pos, overlay_y_pos])

    screen.blit(img_frame_counter, [frame_counter_x_pos, frame_counter_y_pos])

    if not frc_success or dash_gap > 10 or second_6_gap > 4:
        # Standard I-No sprites
        if not first_ino_drawn:
            screen.blit(img_ino_p1, [ino_x_pos, ino_y_pos])

        if side == 'p2' and side_prev == 'p1':
            screen.blit(img_ino_p2, [ino_x_pos, ino_y_pos])
            first_ino_drawn = True

        if side == 'p1' and side_prev == 'p2':
            screen.blit(img_ino_p1, [ino_x_pos, ino_y_pos])

    else:
        # Success I-No sprites
        if not first_ino_drawn:
            screen.blit(img_ino_success_p1, [ino_success_x_pos, ino_success_y_pos])

        if side == 'p2' and side_prev == 'p1':
            screen.blit(img_ino_success_p2, [ino_success_x_pos, ino_success_y_pos])
            first_ino_drawn = True

        if side == 'p1' and side_prev == 'p2':
            screen.blit(img_ino_success_p1, [ino_success_x_pos, ino_success_y_pos])

    screen.blit(img_speech, [speech_x_pos, speech_y_pos])

    ui_btn_help.draw(screen)
    ui_btn_sfx.draw(screen)    
    ui_btn_hitstop.draw(screen)
    ui_btn_config.draw(screen)
    ui_btn_side_switch.draw(screen)

    if hitstop_changed:
        textPrintTips.print(screen, "Hitstop offset changed.", color=(0, 0, 0))
        hitstop_changed += 1
        if hitstop_changed >= 180:
            hitstop_changed = 0

    if config_changed:
        textPrintTips.print(screen, "Button config loaded.", color=(0,0,0))
        config_changed += 1
        if config_changed >= 180:
            config_changed = 0

    



    if debug: 
        # Get count of joysticks
        joystick_count = pygame.joystick.get_count()
    
        textPrint.print(screen, "Number of joysticks: {}".format(joystick_count))
        textPrint.indent()
    
        joystick = pygame.joystick.Joystick(0)
        # For each joystick:
        for i in range(joystick_count):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
    
            textPrint.print(screen, "Joystick {}".format(i))
            textPrint.indent()
    
            # Get the name from the OS for the controller/joystick
            name = joystick.get_name()
            textPrint.print(screen, "Joystick name: {}".format(name))
    
            # Usually axis run in pairs, up/down for one, and left/right for
            # the other.
            axes = joystick.get_numaxes()
            textPrint.print(screen, "Number of axes: {}".format(axes))
            textPrint.indent()
    
            for i in range(axes):
                axis = joystick.get_axis(i)
                textPrint.print(screen, "Axis {} value: {:>6.3f}".format(i, axis))
            textPrint.unindent()
    
            buttons = joystick.get_numbuttons()
            textPrint.print(screen, "Number of buttons: {}".format(buttons))
            textPrint.indent()
    
            for i in range(buttons):
                button = joystick.get_button(i)
                textPrint.print(screen, "Button {:>2} value: {}".format(i, button))
            textPrint.unindent()
    
            # Hat switch. All or nothing for direction, not like joysticks.
            # Value comes back in an array.
            hats = joystick.get_numhats()
            textPrint.print(screen, "Number of hats: {}".format(hats))
            textPrint.indent()
    
            for i in range(hats):
                hat = joystick.get_hat(i)
                textPrint.print(screen, "Hat {} value: {}".format(i, hat))
            textPrint.unindent()
    
            textPrint.unindent()

    # Have only 1 plugged in when starting, TODO make a class and put this into a library, call all these checks
    """ Begin Xbox 360 """
    joystick_check = pygame.joystick.get_count()
    if joystick_check == 0:
        print('No controller detected. Please connect controller before running program. Exiting safely.')
        break
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    name = joystick.get_name()
    if debug: textPrint.print(screen, "{}".format(name))

    axis = joystick.get_axis(2)

    buttons = joystick.get_numbuttons()
    input_btns = []
    for button_num in xb_button_map:
        button = joystick.get_button(button_num)

        if button and button_num in xb_valid_button_nums:
            input_btns.append(gg_button_map.get(xb_button_map[button_num], ''))

            if debug: 
                textPrint.print(screen, "{}".format(xb_button_map[button_num]))

            if button_num != 6: # If it's any button other than Select, blit to overlay
                screen.blit(overlay_btn, [overlay_x_pos+overlay_map[button_num][0]-overlay_x_offset, overlay_y_pos+overlay_map[button_num][1]-overlay_y_offset])
            elif button_num == 6 and not side_switch_btn_pressed:
                side_prev = side 
                if side == 'p1': side = 'p2'
                else: side = 'p1'
                
                side_switch_btn_pressed = True
            xb_held_buttons[xb_button_map[button_num]] += 1
            if debug:
                print(xb_held_buttons[xb_button_map[button_num]], xb_button_map[button_num])

    if 'select' not in input_btns:
        side_switch_btn_pressed = False


    axis = round(axis, 3)

    if axis == 0.996:
        input_btns.append(gg_button_map.get('LT', ''))

        if debug:
            textPrint.print(screen, "{}".format(xb_axis_map[axis]))

        screen.blit(overlay_btn, [overlay_x_pos+overlay_map[axis][0]-overlay_x_offset, overlay_y_pos+overlay_map[axis][1]-overlay_y_offset])
        xb_held_buttons[xb_axis_map[axis]] += 1
        if debug:
            print(xb_held_buttons[xb_axis_map[axis]], xb_axis_map[axis])
    elif axis == -0.996:
        input_btns.append(gg_button_map.get('RT', ''))

        if debug:
            textPrint.print(screen, "{}".format(xb_axis_map[axis]))

        screen.blit(overlay_btn, [overlay_x_pos+overlay_map[axis][0]-overlay_x_offset, overlay_y_pos+overlay_map[axis][1]-overlay_y_offset])
        xb_held_buttons[xb_axis_map[axis]] += 1
        if debug:
            print(xb_held_buttons[xb_axis_map[axis]], xb_axis_map[axis])   

    # Get directional input
    hat = joystick.get_hat(0)
    if debug:
        textPrint.print(screen, "{}".format(xb_dir_map[hat]))

    input_btns.append(str(xb_dir_map[hat]))

    if debug:
        textPrint.print(screen, "{}".format("".join([str(item) for item in input_btns])))
    
    # TODO fix for hold directions ; charge moves
    if xb_dir_map[hat] != 5 and xb_dir_map[hat] != prevDir:
        pass

    screen.blit(overlay_balltop, [overlay_x_pos+overlay_map[hat][0]-overlay_x_offset, overlay_y_pos+overlay_map[hat][1]-overlay_y_offset])
    prevDir = xb_dir_map[hat]
     
    """ End Xbox 360 """


    """ Start Buffer input processing """
    
    
    
    buffer[buf_ptr] = input_btns
    if buf_ptr == 0:
        buffer[0].append('*') # Special case for beginning to detect HCL

    prev_fsm_hcl_states[buf_ptr] = fsm_hcl_state

    if fsm_hcl_state < 7 and capture_trigger == "hcl": # If not currently in an HCL
        fsm_hcl_state = fsm_hcl(buffer, fsm_hcl_state, input_btns, side)
        if all(fsm_hcl_state == x for x in prev_fsm_hcl_states):
            fsm_hcl_state = 0

    elif fsm_hcl_state < 7 and capture_trigger == "k":
        if 'k' in input_btns:
            fsm_hcl_state = 7

    elif fsm_hcl_state < 7 and capture_trigger == "s":
        if 's' in input_btns:
            fsm_hcl_state = 7

    elif fsm_hcl_state < 7 and capture_trigger == "h":
        if 'h' in input_btns:
            fsm_hcl_state = 7

    

    buf_ptr = (buf_ptr + 1) % buf_size

    if fsm_hcl_state == 7: # You're in an HCL/pressed a normal to cancel into HCL (depending on hitstop selected)
        #if post_hcl_frame_num == 0:
        #    post_hcl_frame_num = 1

        if hitstop_delay >= hitstop:
            post_hcl_buffer, post_hcl_state = tick_hcl(post_hcl_frame_num, post_hcl_buffer, post_hcl_state, input_btns, side)

            post_hcl_frame_num += 1

            prev_max_post_hcl_state = max(prev_max_post_hcl_state, post_hcl_state)

        else:
            hitstop_delay += 1



        if post_hcl_frame_num < post_hcl_frames:
            textPrintEval.print(screen, "Inputs after HCL {}".format("".join(post_hcl_buffer)))

        #if post_hcl_frame_num >= post_hcl_frames:
        else:
            # Look for next hcl
            fsm_hcl_state = 0

            # Flush post hcl buffer and reset post hcl state
            if 'f' in post_hcl_buffer and frc_frame1 <= post_hcl_buffer.index('f') <= frc_frame2:
                frc_success = True
            else:
                frc_success = False

            if 'f' in post_hcl_buffer:
                frc_frame_attempt = post_hcl_buffer.index('f')
            else:
                frc_frame_attempt = 999

            if post_hcl_buffer.count('6') == 2:
                dash_frames = [index for index, char in enumerate(post_hcl_buffer) if char == '6']
                dash_gap = dash_frames[1] - dash_frames[0]
                second_6_gap = dash_frames[1] - frc_frame_attempt

            else:
                dash_gap = 999
                second_6_gap = 999

            prev_post_hcl_buffer = post_hcl_buffer.copy()
            post_hcl_buffer = ['.']*post_hcl_frames
            post_hcl_state = 0
            post_hcl_frame_num = 0
            prev_max_post_hcl_state = 0
            first_attempt = False
            hitstop_delay = 0
    
    if debug:
        textPrintStates.print(screen, "fsm_hcl_state {}".format(str(fsm_hcl_state)))
        textPrintStates.print(screen, "buf {}".format(buffer))
        textPrintStates.print(screen, "prev_fsm_hcl_states {}".format(prev_fsm_hcl_states))
        textPrintStates.print(screen, "post_hcl_state {}".format(post_hcl_state))
        textPrintStates.print(screen, "prev_max_post_hcl_state {}".format(prev_max_post_hcl_state))

    #textPrintEval.print(screen, "Inputs after HCL {}".format("".join(post_hcl_buffer)))

    if frc_success:
        frc_mark = 'X'
    else:
        frc_mark = ' '

    if dash_gap <= 10:
        dash_mark = 'X'
    else:
        dash_mark = ' '
    
    if second_6_gap <= 4:
        second_6_mark = 'X'
    else:
        second_6_mark = ' '

    if fsm_hcl_state != 7:
        textPrintEval.print(screen, "Inputs after HCL {}".format("".join(prev_post_hcl_buffer)))

    textPrintEval.print(screen, "[{}] FRC frame {}f ≤ t ≤ {}f  : {}".format(frc_mark, str(frc_frame1), str(frc_frame2), str(frc_frame_attempt)))
    textPrintEval.print(screen, "[{}] Dash input gap ≤ 10f     : {}f".format(dash_mark, str(dash_gap)))
    textPrintEval.print(screen, "[{}] FRC/2nd 6 input gap ≤ 4f : {}f".format(second_6_mark, str(second_6_gap)))
    
    """ End Buffer input processing """

    """ Tip display start """
    if not frc_success and frc_frame_attempt != 999 and not first_attempt:
        if frc_frame_attempt < min(frc_frame1, frc_frame2):
            textPrintTips.print(screen, "FRC {}f later.".format(str(frc_frame1 - frc_frame_attempt)), (0, 0, 0))
        else:
            textPrintTips.print(screen, "FRC {}f sooner.".format(str(frc_frame_attempt - frc_frame2)), (0, 0, 0))

    if dash_gap > 10 and dash_gap != 999 and not first_attempt:
        textPrintTips.print(screen, "Tighten dash by {}f.".format(str(dash_gap - 10)), (0, 0, 0))

    if second_6_gap > 4 and second_6_gap != 999 and not first_attempt:
        textPrintTips.print(screen, "Tighten FRC6 by {}f.".format(str(second_6_gap - 4)), (0, 0, 0))

    if frc_success and dash_gap <= 10 and second_6_gap <= 4 and not first_attempt:
        screen.blit(img_kimochi, [kimochi_x_pos, kimochi_y_pos])

    """ Tip display end """

    display_fps(fonts, (x_margin, y_margin))

    """ Help display start """
    if display_help_window:
        ui_win_help_border.draw(screen)
        ui_win_help.draw(screen)
        ui_btn_close_help.draw(screen)
        textPrintHelp.print(screen, 
            "1. Ensure your button config is set correctly. The timing is set to trigger") 
        textPrintHelp.print(screen,
            "on detection of an HCL input, K input, or S input for Hitstop Offsets") 
        textPrintHelp.print(screen,
            "'raw', '5k', and '2s', respectively. See the bundled config.txt file.")
        textPrintHelp.print(screen, "")

        textPrintHelp.print(screen,
            "2. Choose the HITSTOP OFFSET setting based on if you want to practice HCL")
        textPrintHelp.print(screen,
            "6FRC6 timing 'raw' (with no hitstop, as if the HCL input was completed")
        textPrintHelp.print(screen,
            "after the hitstop of 5H ended), or when cancelled from a 5k or 2s on the")
        textPrintHelp.print(screen,
            "first possible frame.")
        textPrintHelp.print(screen, "")

        textPrintHelp.print(screen,
            "3. After attempting an HCL 6FRC6, the 'inputs after HCL' shows the next")
        textPrintHelp.print(screen,
            "28 frames of inputs. Adjust and develop a feel for the timing with the")
        textPrintHelp.print(screen,
            "feedback provided.")
        textPrintHelp.print(screen, "")

        textPrintHelp.print(screen,
            "* You can switch sides with whatever button you mapped to select/back.")
        textPrintHelp.print(screen,
            "* Due to Pygame limitations, detected inputs may be ≤ 2f early.")
        textPrintHelp.print(screen,
            "* Full documentation and more at https://github.com/jcr179/heaven_or_hcl")
        textPrintHelp.print(screen, "")

        textPrintHelp.print(screen,
            "Thank you @YoJimbo0321, @kurushii_drive, FGC@UCLA, the #i-no channel at the")
        textPrintHelp.print(screen,
            "GGXX+R discord, anyone using and improving this tool, and my fam & friends.")
        textPrintHelp.print(screen, "")

        textPrintHelp.print(screen,
            "# " + version + ", by Zenryoku#2982 from FGC@UCLA.")

        textPrintHelp.reset(newline_spacing=12)
    """ Help display end"""

    #pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(0, surf_y_size-300, surf_x_size, 5))

    pygame.display.update()
    clock.tick(fps)

    buttonPressed = False 
    buttonReleased = False

        

        