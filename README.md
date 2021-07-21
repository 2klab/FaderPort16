# FaderPort16
Presonus FaderPort16 or FaderPort8 Interface including Scribble text

    Midi implementation of the Presonus FaderPort16 (and FaderPort8)
    Features include:
    - Led and RGB buttons
    - Mini-screens text - Scribble text
    - PanParam and Session Encoder rotating buttons can return values greater
    than +1/-1 when turned quickly
    - Channel strips (8 or 16):
        - Mute/Solo
        - Select
        - Fader touch
        - Fader move
        - mini-screens - scribble screens text
        - Toggle state
    - Port names are typically named like: 'PreSonus FP16 1'. To be set in port_name attribute

    Prints to console currently, so to be overridden to fit specifics
    Mido numbers channels 0 to 15 instead of 1 to 16, same idea is applied here

    - Demos included
