# Heaven or HCL
A training tool to help GGXXAC+R I-no players develop their execution.

## What is this tool?
Heaven or HCL (HoHCL, hohcl) is a minimal application that is meant to be running alongside an instance of Guilty Gear XX Accent Core Plus R (+R). This is intended to be a utility that helps measure the timing of a player's inputs relative to the required timings needed for I-no players to execute a horizontal chemical love (hcl) dash-split force roman cancel (6frc6), which is a difficult but important barrier to overcome when maximizing I-no's destructive potential.

## How do I use it?
To download the program from github, click the green "Code" button in the top-right of this window displaying this file. Click "Download ZIP" and take note of where on your machine it was downloaded to. Unzip the zip file to the directory of your choice. Navigate to the heaven_or_hcl directory. **Plug in your controller before starting the program; it will not work if you don't have a controller plugged in**. Open the "Heaven or HCL" executable file. Now you're ready to rock!

The main display consists of a sprite of I-no with timing adjustment suggestions communicated through her speech bubble. There is a stick/button layout overlay to give feedback of what inputs are being read by the program. Below that is a timeline showing frame-by-frame inputs read after the start of an hcl. Details of how this is detected and timed are explored later in this README. Below the timeline is a checklist of conditions needed to be met for an hcl 6frc6 to be executed successfully, updated based on your last attempt at a hcl 6frc6.

Have hohcl open while you have +R open and focused. For now, you'll have to set +R to windowed/borderless (this can introduce a little input lag...) or set to fullscreen and have hohcl open in a different monitor. *(I will see if I can improve this later on.)* You can start training mode and play as normal, while referring to the trainer tool to see how to adjust your timing to land that sweet hcl 6frc6!

## How do I change settings and what do they do?

- SIDE SWITCH: The program tries to detect when you input an hcl. Clicking this button (or select on your controller) changes the side the program thinks you're on.
- LOAD CONFIG: Refreshes the button config used by the program based on the contents of the config.txt file. 
- HITSTOP: Click to cycle between making the program change timings based on whether you're doing the hcl raw - with no hitstop, like after the hitstop of 5h ends - or cancelled from 5k or 2s as soon as the special move buffer allows. The timing of the program's input display is tied to different triggers for each HITSTOP setting. For the Raw setting, the timeline starts immediately upon detecting an hcl. For the 5k and 2s settings, it's triggered by input from the k and s buttons, respectively.
- SFX: Toggle an audio cue track synced to the button timing for an hcl 6frc6. Might be helpful to certain peoples' learning styles. Details later in this doc.
- HELP: Display an abridged version of this README along with other notes.

## About the timeline
The timeline here refers to the sequence of dots or lines following the text "Inputs after HCL" just below I-no. The numbers above the marks indicate frames of the hcl. There is a small blue streak over frames 16 and 17 to indicate that this is your timing window for a successful frc. The timeline will "start" upon detection of an hcl, or a set amount of time after pressing k or s, depending on if your HITSTOP is set to Raw, 5k, or 2s, respectively. 

A **6** on the timeline indicates a 6 input (in numpad notation); a forward input. An **f** on the timeline indicates an frc input (any 3 buttons excluding Dust). Other kinds of inputs (other directions, single button inputs) are ignored: the idea is to have the timeline display only inputs relevant to an hcl 6frc6 for legibility. 

The timeline will stay displaying your last attempt until you're detected making another attempt.

Underneath the timeline are the three conditions needed to pull off an hcl 6frc6.
1. The frame where FRC was input must be frame 16 or 17
2. The 6 inputs used to produce a forward dash are at most 10 frames (10f) apart
3. The time between the FRC input and the 2nd 6 needed to produce a forward dash are at most 4f apart

I-no will give you simple pointers interpreting your performance of these criteria so you don't have to parse everything on your own.

If you nail it, I-no will say 気持ち！ (Kimochi!) (It feels good!)

## More about using config.txt and mapping buttons
The file config.txt is what the program reads to know your button mappings. 
You won't need to touch this if you use the default rainbow layout. (p, k, s, h, d)

`type=[xbox, ps4]`
The value of this can be either `xbox` or `ps4`, and is `xbox` by default. You can generally ignore this as the program tries to detect what type your controller is, but you can set to one of these values based on your controller type if the program guesses wrong.

`config_override[0, 1]`
On the off chance that your xbox controller is detected as a ps4 controller or vice versa, set this to 1 so that the `type` value you set above will be used. Otherwise just leave it to 0 so the program can automatically detect your controller type.

`k=xbox_[X, A, Y, RB, RT, Back, LB, Start]`
Set xbox_`anything from the above list` to set what button on your xbox controller you want to be bound to k (kick). The same idea follows for buttons p, s, h, d, back/select. If you're using a ps4 controller you can ignore this.

`k=ps4_[Square, Cross, Triangle, Circle, R1, R2, L1, L2, Start, Back]`
Set ps4_`anything from the above list` to set what button on your ps4 controller you want to be bound to k (kick). The same idea follows for buttons p, s, h, d, back/select. If you're using an xbox controller you can ignore this.


## What's up with all this HITSTOP stuff?
Depending on what you cancel into hcl with, the timing for the frc will be different because of variable amounts of hitstop. If you do 5k hcl, you will see less hitstop than 2s hcl. So, setting the HITSTOP appropriately accounts for these variations in hitstop by delaying when the timeline starts recording inputs to reflect the delay in hcl startup from being cancelled into from a normal.

Thanks to the special move buffer, if you input the hcl during the hitstop of a special cancellable normal, the hcl comes out at the same frame - the first frame it can come out. So for hitstop settings 5k and 2s, the triggering event (what sets of the delayed timeline) is the press of k or s. The startup and hitstop of the attack is constant (though I assume the attack hits on the first active frame, i.e. not meaty) and that's what's used to know many frames to delay the hcl startup by.

The Raw setting is a special case: to be used for when you're *not in hitstop*. So the timeline starts instantly when using this setting. Meant to be used when doing hcl after the hitstop of 5h ends, or when practicing just the frc.

## More about the SFX track
16f, or 266.67 ms in a 60fps game, works out to 225 bpm. I use 112.5 bpm. So if you did an hcl on the 1 of a beat (the k completing the input 632146k lands on the 1), the frc is on the 2 of the beat (assuming Raw hitstop, i.e. not cancelled from 5k or 2s). That's what you hear in the SFX track.

In one loop of the track, you hear a kick (bass) and a blip on the 1, then three blips, then a higher percussive sound. The kick and blip is where you would complete the hcl input, and the following 3 blips are the timing for the 6, frc, 6. Precisely, the first 6 is 4f before the frc (which is on frame 16) and the second 6 is 4f after the frc - the symmetrical timings relative to the frc were chosen to try and make the beat sound more musical and tight. The higher pecussive sound just exists to fill the space and help make the timing/anticipation of the next repetition easier to place. 

If you want to mess with the SFX track or practice with just that, it's in the *resources* folder.

## Usage examples
You can use this tool just to practice your frc timing of hcl. Set HITSTOP to Raw and do hcls from a neutral state. Try pressing frc when the timeline passes the blue streak, like those games at arcades that had a trail of lights arranged in a circle where you had to press the button when the light passed over a certain marker to get maximum tickets.

With HITSTOP set to Raw, you can also practice TK HCL 6frc6. Or you can do your jump install combo into 5h, do 63214 during the 5h and 6k when the hitstop ends to initialize your hcl.

## Accuracy and precision of HoHCL
This was made with Pygame. Pygame has inherent limitations in that its clock only has millisecond accuracy. Since in a 60 fps game each frame takes 16.667 ms, Pygame can't get exactly 60 fps (since it can only make clocks of 16 or 17 ms). So you'll see the program typically run at 59 fps or 58 fps. Furthermore, sub-frame inputs are also a factor (inputs that take less than a frame) that make detection of an hcl difficult.

This leads to some errors in detection. I tested the performance of the program's detection by recording some inputs and reviewing them with the frame-by-frame input viewer in +R's replay mode. A test here consisted of doing an hcl and attempting an frc. Based on 35 such tests, HoHCL detected an input at most 2f earlier than actual for all 35 tests. 

The program will throw some false positives and false negatives. That's unavoidable. However, the program can still be useful as a tool to calibrate your timing in "the right direction", to keep yourself warm between matches, and to help you land your very first few hcl 6frc6s and develop your own feel. *This program is not meant to be a highly accurate performance tracker, but more as a guide.*

## Updates in the future...
- Keyboard support
- Hitstop offset support for jumping normals
- SFX for different hitstop offsets
- Force window on top of focused +R window