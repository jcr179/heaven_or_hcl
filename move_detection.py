# frames for frc
frc_frame1 = 16
frc_frame2 = 17

timeline_tick_char = '|'
frc_tick_char = 'X'
buf_6_size = 4 # buffer between 6 inputs during post_hcl input tracking 
timeline_tick_spacing = 5 # visual aid for reading input timeline's frames, place a mark every X frames

# side switching
dirmap_p1 = {
    '1': '1',
    '2': '2',
    '3': '3',
    '4': '4',
    '5': '5',
    '6': '6',
    '7': '7',
    '8': '8',
    '9': '9'
}
dirmap_p2 = {
    '1': '3',
    '2': '2',
    '3': '1',
    '4': '6',
    '5': '5',
    '6': '4',
    '7': '9',
    '8': '8',
    '9': '7'
}
dirmap = {
    'p1' : dirmap_p1,
    'p2' : dirmap_p2
}

def fsm_hcl(buffer, input_state, input_btns, side):
    prereqs = ['*', '6', '3', '2', '1', '4', '6']
    prereqs[1:] = [dirmap[side][x] for x in prereqs[1:]]
    #print(prereqs)

    #print(input_btns)
    if any(prereqs[input_state] in x for x in buffer) and input_state == 0 and dirmap[side]['6'] in input_btns:
        return 1

    # from 6 to 3 or 2
    elif any(prereqs[input_state] in x for x in buffer) and input_state == 1 and dirmap[side]['3'] in input_btns:
        return 2
    elif any(prereqs[input_state] in x for x in buffer) and input_state == 1 and dirmap[side]['2'] in input_btns:
        return 3

    elif any(prereqs[input_state] in x for x in buffer) and input_state == 2 and dirmap[side]['2'] in input_btns: 
        return 3

    # from 2 to 1 or 4
    elif any(prereqs[input_state] in x for x in buffer) and input_state == 3 and dirmap[side]['1'] in input_btns:
        return 4
    elif any(prereqs[input_state] in x for x in buffer) and input_state == 3 and dirmap[side]['4'] in input_btns:
        return 5

    elif any(prereqs[input_state] in x for x in buffer) and input_state == 4 and dirmap[side]['4'] in input_btns:
        return 5

    # Might jump from state 5 to 6 or 7 depending on if 6k happens on same frame
    elif any(prereqs[input_state] in x for x in buffer) and input_state == 5 and dirmap[side]['6'] in input_btns:
        return 6
    elif any(prereqs[input_state] in x for x in buffer) and input_state == 5 and dirmap[side]['6'] in input_btns and 'k' in input_btns:
        return 7

    elif any(prereqs[input_state] in x for x in buffer) and input_state == 6 and 'k' in input_btns:
        return 7

    return input_state

def tick_hcl(frame_num, timeline, input_state, input_btns, side):

    output_state = input_state
    input_saved = False

    # Have to let go of 6 (or 3 or 9) from HCL
    if input_state == 0 and not any(item in [dirmap[side]['3'], dirmap[side]['6'], dirmap[side]['9']] for item in input_btns):
        output_state = 1

    # 1st 6
    elif input_state == 1 and dirmap[side]['6'] in input_btns:
        output_state = 2
        timeline[frame_num] = '6'
        input_saved = True

    # Let go of 6 again to let another 6 be a valid forward dash BEFORE frc
    elif input_state == 2 and not any(item in [dirmap[side]['3'], dirmap[side]['6'], dirmap[side]['9']] for item in input_btns):
        output_state = 3

    # FRC
    elif input_state == 3 and (set(['p', 'k', 's']).issubset(input_btns) or 
            set(['p', 'k', 'h']).issubset(input_btns) or 
            set(['k', 's', 'h']).issubset(input_btns)):
        if frc_frame1 <= frame_num <= frc_frame2:
            output_state = 4
        if 'f' not in timeline:
            timeline[frame_num] = 'f'
            input_saved = True
        
    # 2nd 6
    elif input_state == 4 and dirmap[side]['6'] in input_btns:
        try:
            dash1_frame = timeline.index('6')
        except ValueError:
            dash1_frame = 0

        try:
            frc_frame = timeline.index('f')
        except ValueError:
            frc_frame = 0

        if frame_num - dash1_frame <= 10 and frame_num - frc_frame <= 4:
            output_state = 5

        if timeline.count('6') <= 1:
            timeline[frame_num] = '6'
            input_saved = True

    # track frc success regardless of 6frc6 attempt
    if (set(['p', 'k', 's']).issubset(input_btns) or set(['p', 'k', 'h']).issubset(input_btns) or set(['k', 's', 'h']).issubset(input_btns)) and 'f' not in timeline:
        timeline[frame_num] = 'f'
        input_saved = True

    # Include all forward inputs after they first let go of 6
    if input_state >= 1 and frame_num - buf_6_size >= 0 and dirmap[side]['6'] in input_btns:
        buf_6 = timeline[frame_num-buf_6_size:frame_num] 
        if all([x != '6' for x in buf_6]):

            timeline[frame_num] = '6'
            input_saved = True

    if not input_saved and (frc_frame1 <= frame_num <= frc_frame2):
        timeline[frame_num] = frc_tick_char

    elif not input_saved and frame_num % timeline_tick_spacing:
        timeline[frame_num] = '-'

    elif not input_saved and frame_num % timeline_tick_spacing == 0:
        timeline[frame_num] = timeline_tick_char

    

    

    
    
        
    """
    print('FRAME ', frame_num, ': ' + str(input_state))
    print('\tinput_btns: ', input_btns)
    print('\t\t', set(['p', 'k', 's']).issubset(input_btns))
    print('\t\t', set(['p', 'k', 'h']).issubset(input_btns))
    print('\t\t', set(['k', 's', 'h']).issubset(input_btns))
    """

    return timeline, output_state