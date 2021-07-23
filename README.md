# FaderPort16
Presonus FaderPort16 or FaderPort8 Interface including Scribble text

    Midi implementation of the Presonus FaderPort16 and FaderPort8
    The FaderPort is well designed: it was easy to python it.
    Features include:
    - Led and RGB buttons
    - Mini-screens text - Scribble text
    - PanParam and Session Encoder rotating buttons return values greater than +1/-1 
    when turned quickly
    - Channel strips 16 or 8 for the FaderPort8:
        - Mute/Solo
        - Select
        - Fader touch
        - Fader move
        - mini-screens - scribble screens text
        - Toggle state
    - Left Shift is current
    - Right Shift is toggle 

    Prints to console currently, so to be overridden to fit specifics
    Mido numbers channels 0 to 15 instead of 1 to 16, same idea is applied here

    - Demos included
