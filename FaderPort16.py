import re
import mido
import time
from random import random
from itertools import cycle


class ChannelStrip(object):
    muted: bool = False
    soloed: bool = False
    fader_value: int = 0
    panparam_value: int = 0
    text: str = ""


class Button(object):
    def __init__(self, group, name, id_hex, led_type):
        """LED  type: 0=none, 1=LED, 2=RGB"""
        self.group: str = group
        self.name: str = name
        self.id_hex: int = id_hex
        self.led_type: int = led_type
        self.toggled: bool = False

    # TODO:Add properties like leds and inherit from mido to set them

    def group_index(self):
        """:returns the Index of the button in its group"""
        bnames = self.get_groupnames()
        return bnames.index(self.name)

    def get_groupnames(self):
        """:returns group of button names"""
        bnames = []
        for b in _ButtonList:
            if b.group == self.group:
                bnames.append(b.name)
        return bnames

    def get_buttons_from_group(self):
        """:returns all Button of a group"""
        buttons = []
        for b in _ButtonList:
            if b.group == self.group:
                buttons.append(b)
        return buttons

    def set_group_led(self, channel, mode):
        pass


_ButtonList = [
    # Transport (done)
    Button("Transport", 'Record', 0x5f, 1),
    Button("Transport", 'Loop', 0x56, 1),
    Button("Transport", 'Stop', 0x5d, 1),
    Button("Transport", 'Fast Fwd', 0x5c, 1),
    Button("Transport", 'Rewind', 0x5b, 1),
    Button("Transport", 'Play', 0x5e, 1),

    # Session Navigator (done)
    Button("SessionNavigator", "Channel", 0x36, 1),
    Button("SessionNavigator", "Zoom", 0x37, 1),
    Button("SessionNavigator", "Scroll", 0x38, 1),
    Button("SessionNavigator", "Bank", 0x39, 1),
    Button("SessionNavigator", "Master", 0x3a, 1),
    Button("SessionNavigator", "Click", 0x3b, 1),
    Button("SessionNavigator", "Section", 0x3c, 1),
    Button("SessionNavigator", "Marker", 0x3d, 1),

    Button("SessionNavigator", 'Prev', 0x2e, 1),
    Button("SessionNavigator", 'Next', 0x2f, 1),
    Button("SessionNavigator", 'EncoderPush', 0x53, 0),

    # Mix management (done)
    Button("MixManagement", 'Audio', 0x3e, 2),
    Button("MixManagement", 'VI', 0x3f, 2),
    Button("MixManagement", 'Bus', 0x40, 2),
    Button("MixManagement", 'VCA', 0x41, 2),
    Button("MixManagement", 'All', 0x42, 2),
    Button("MixManagement", 'ShiftR', 0x06, 1),  # ERROR in user manual 0x06

    # Automation
    Button("Automation", 'Read', 0x4a, 1),
    Button("Automation", 'Write', 0x4b, 1),
    Button("Automation", 'Trim', 0x4c, 1),
    Button("Automation", 'Touch', 0x4d, 1),
    Button("Automation", 'Latch', 0x4e, 1),
    Button("Automation", 'Off', 0x4f, 1),

    # Fader Mode Buttons (done)
    Button("FaderMode", 'Track', 0x28, 1),
    Button("FaderMode", "EditPlugins", 0x2b, 1),
    Button("FaderMode", 'Sends', 0x29, 1),
    Button("FaderMode", 'Pan', 0x2a, 1),

    # General Controls (done)
    Button("General", 'PanParamPush', 0x20, 0),
    Button("General", 'ARM', 0x00, 1),
    Button("General", 'SoloClear', 0x01, 1),
    Button("General", 'MuteClear', 0x02, 1),
    Button("General", 'ShiftL', 0x46, 1),  # ERROR in user manual
    Button("General", 'Bypass', 0x03, 2),
    Button("General", 'Macro', 0x04, 2),
    Button("General", 'Link', 0x05, 2),
]

_button_from_id_hex = {b.id_hex: b for b in _ButtonList}


def button_from_id_hex(id_hex: int) -> Button:
    """
    Given a button id_hex value return the corresponding button
    :param id_hex: The value emitted by a pushed button
    :return: a Button
    """
    return _button_from_id_hex.get(id_hex, None)


def hexcolor_to_rgbcc(hexcolor):
    """ Converts an Hex color to its equivalent Red, Green, Blue
            Converse = hexcolor = (r << 16) + (g << 8) + b
    """
    r = (hexcolor >> 16) & 0x7F
    g = (hexcolor >> 8) & 0x7F
    b = hexcolor & 0x7F
    return r, g, b


def strip_is_mute(note) -> bool:
    return get_channel_mute(note) is not None


def strip_is_solo(note) -> bool:
    return get_channel_solo(note) is not None


strip_mute_notes = [0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x78, 0x79, 0x7a, 0x7b, 0x7c, 0x7d, 0x7e, 0x7f]


def get_channel_mute(note):
    if note in strip_mute_notes:
        return strip_mute_notes.index(note)
    else:
        return None


def get_mute_note_fromchannel(channel: int):
    return strip_mute_notes[channel]


strip_solo_notes = [0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f, 0x50, 0x51, 0x52, 0x58, 0x54, 0x55, 0x59, 0x57]


def get_channel_solo(note):
    if note in strip_solo_notes:
        return strip_solo_notes.index(note)
    else:
        return None


strip_select_notes = [0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f, 0x07, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26,
                      0x27]


def get_channel_select(note):
    if note in strip_select_notes:
        return strip_select_notes.index(note)
    else:
        return None


def strip_is_select(note):
    return get_channel_select(note) is not None


def strip_is_fadertouch(note):
    return get_channel_fadertouch(note) is not None


strip_fadertouch_notes = [0x68, 0x69, 0x6a, 0x6b, 0x6c, 0x6d, 0x6e, 0x6f, 0x70, 0x71, 0x72, 0x73, 0x74, 0x75, 0x76,
                          0x77]


def get_channel_fadertouch(note):
    if note in strip_fadertouch_notes:
        return strip_fadertouch_notes.index(note)
    else:
        return None


def rotate_convert(value) -> int:
    """
    :param value:midi values: 1-63 plus
        65-127 minus
    :return: value to add
    """
    if value & 64:
        return -(value - 64)
    else:
        return value


def getvalue_fromstate(state):
    value = 0x00
    if state == 1:
        value = 0x7f
    elif state == 2:
        value = 0x01
    return value


def set_strip_valuebar(self, channel, mode, value):
    vb_number = channel
    if vb_number <= 7:
        note = 0x30 + vb_number
    else:
        note = 0x40 + vb_number
    self._outport.send(mido.Message.from_bytes([0x90, note, value]))


class ScribbleStripMode:
    Default = 0
    AlternativeDefault = 1
    SmallText = 2
    LargeText = 3
    LargeTextMetering = 4
    DefaultTextMetering = 5
    MixedText = 6
    AlternativeTextMetering = 7
    MixedTextMetering = 8
    Menu = 9


class ValueBarMode:
    Normal = 0
    Bipolar = 1
    Fill = 2
    Spread = 3
    Off = 4


def clamp(val, min_, max_): return min_ if val < min_ else max_ if val > max_ else val


def print_input_output_ports():
    for v in mido.get_input_names():
        print(f"input port={v}")
    for v in mido.get_output_names():
        print(f"output port={v}")


class FaderPort16:
    """
    Midi implementation of the Presonus FaderPort16 (see FaderPort8)
    Features include:
    - Led and RGB buttons
    - Mini-screens text
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
    """

    def __init__(self):
        self._sysexhdr = [0xf0, 0x00, 0x01, 0x06, 0x16]
        self._inport = None
        self._outport = None
        self.port_name_starts_with = 'PreSonus FP16'
        self.channel_number = 16
        self.max_fader_value = 1023
        self.max_rotation_value = 127
        self._toggled_on = []
        self.selected_channel = 0
        self.shiftL = False
        self.shiftR = False
        self.end_demo = False
        self.strips = []
        for loop in range(self.channel_number):
            self.strips.append(ChannelStrip())

    def __enter__(self):
        self.on_opening()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.on_closing()

    def on_opening(self):
        """
        """
        for name in mido.get_input_names():
            if re.match(self.port_name_starts_with, name, re.I):
                self._inport = mido.open_input(name)
                break

        for name in mido.get_output_names():
            if re.match(self.port_name_starts_with, name, re.I):
                self._outport = mido.open_output(name)
                break

        self._inport.callback = self._midi_message_callback

    def on_closing(self):
        self._inport.callback = None
        self.set_defaults()
        self.set_all_buttonleds_off()
        # self.init_strip()
        self._outport.reset()
        self._inport.close()
        self._outport.close()

    def _midi_message_callback(self, msg):
        """MIDI messages"""
        if msg.type == 'note_on':
            button = button_from_id_hex(msg.note)
            if strip_is_fadertouch(msg.note):
                self.on_strip_fadertouch(get_channel_fadertouch(msg.note), msg.velocity != 0)
            elif strip_is_mute(msg.note):
                self.on_strip_mute(get_channel_mute(msg.note), msg.velocity != 0)
            elif strip_is_solo(msg.note):
                self.on_strip_solo(get_channel_solo(msg.note), msg.velocity != 0)
            elif strip_is_select(msg.note):
                self.on_strip_select(channel=get_channel_select(msg.note), pushed=msg.velocity != 0)
            elif button:
                self.on_button_single(button, msg.velocity != 0)
            else:
                print(f"Unknown Button {msg}")
        elif msg.type == 'control_change':
            if msg.control == 60:
                self.on_encoder(channel=self.selected_channel, increment=rotate_convert(msg.value) * 16)
            elif msg.control == 16:
                self.on_panparam(self.selected_channel, increment=rotate_convert(msg.value))
        elif msg.type == 'pitchwheel':
            val: int = int((msg.pitch + 8192) / 16)
            # print(f"val={val} msg={msg}")
            self.on_strip_fadermove(msg.channel, val)
        else:
            print(f'Unhandled:{msg}')

    def on_button_single(self, button: Button, pushed):
        if button.name in ['ShiftL', 'ShiftR']:
            self.on_shift_select(button, pushed)
        elif button.name in ['Next', 'Prev']:
            self.on_strip_select(self.selected_channel + (1 if button.name == 'Next' else -1), pushed)
        elif button.name == 'PanParamPush' and not pushed:
            self.on_panparam(self.selected_channel, 0, True)
        elif button.name == 'EncoderPush' and not pushed:
            self.on_encoder(self.selected_channel, 0, True)
        elif button.name == 'SoloClear':
            self.solo_clear()
        elif button.name == 'MuteClear':
            self.mute_clear()
        elif button.name == 'ARM':
            self.end_demo = True
        elif button.group == 'SessionNavigator':
            self.on_session_navigator_group(button, pushed)
        elif button.group == 'MixManagement':
            self.on_mix_management_group(button, pushed)
        elif button.group == 'FaderMode' and pushed:
            self.on_fadermode_group(button, pushed)
        elif button.group == 'Automation':
            self.set_any_led(button, pushed)
        elif button.group == 'Transport':
            self.set_any_led(button, pushed)

        """
        Specific button pushed or released
        Setting the led on/off is to be handled by each method
            due to the different expected results
        """
        print(f"Button: {button.name} {pushed}")

    #        elif pushed:
    #            self.set_led(button, 1)
    #        else:
    #            self.set_led(button, 0)

    def solo_clear(self):
        for chan in range(self.channel_number):
            self.set_strip_led_solo(chan, 0)
            self.strips[chan].soloed = False

    def mute_clear(self):
        for chan in range(self.channel_number):
            self.set_strip_led_mute(chan, 0)
            self.strips[chan].muted = False

    def on_mix_management_group(self, button, pushed):
        self.set_any_led(button, 1 if pushed else 0)
        if button.name == 'Audio':
            for chan in range(self.channel_number):
                self.set_strip_fader(chan, round(1023 * 0.75))
        elif button.name == 'VI':
            for chan in range(self.channel_number):
                self.set_strip_fader(chan, round(1023 * 0.5))
        elif button.name == 'Bus':
            for chan in range(self.channel_number):
                self.set_strip_fader(15 - chan, int(round(1023) / self.channel_number * chan))
        elif button.name == 'VCA':
            for chan in range(self.channel_number):
                self.set_strip_fader(chan, int(round(1023) / self.channel_number * chan))
        elif button.name == 'All':
            for chan in range(self.channel_number):
                self.set_strip_fader(chan, 0)

    def set_any_led(self, button: Button, state=1):
        """Turns on led on a single button.
        :param button:
        :param state: 0=off, 1=on, 2=flashing
        """
        value = 0x00
        if state == 1:
            value = 0x7f
        elif state == 2:
            value = 0x01
        self._outport.send(mido.Message('note_on', note=button.id_hex, velocity=value))

    def set_strip_fader(self, channel: int, value: int):
        """
        :param channel : channelstrip 0-15
        :param value from 0 to 1023 becomes -8192 to 8176
        """
        if value < 0 or value > self.max_fader_value:
            print(f"Error value = {value}")
            raise ValueError
        if channel < 0 or channel >= self.channel_number:
            raise ValueError
        pitch_val = value * 16 - 8192
        self._outport.send(mido.Message('pitchwheel', channel=channel, pitch=pitch_val))

    def set_strip_led_mute(self, channel: int, state=1):
        """Turns on led on a single button.
        :param channel:
        :param state: 0=off, 1=on, 2=flashing
        """
        value = getvalue_fromstate(state)
        note = strip_mute_notes[channel]
        self._outport.send(mido.Message('note_on', note=note, velocity=value))

    def set_strip_led_solo(self, channel: int, state=1):
        """Turns on led on a single button.
        :param channel:
        :param state: 0=off, 1=on, 2=flashing
        """
        value = getvalue_fromstate(state)
        note = strip_solo_notes[channel]
        self._outport.send(mido.Message('note_on', note=note, velocity=value))

    def set_strip_rgb_select(self, channel, hexcolor=0x1122ff, state=1):
        note = strip_select_notes[channel]
        red, green, blue = hexcolor_to_rgbcc(hexcolor)
        self._outport.send(mido.Message.from_bytes([0x91, note, red]))
        self._outport.send(mido.Message.from_bytes([0x92, note, green]))
        self._outport.send(mido.Message.from_bytes([0x93, note, blue]))
        value = getvalue_fromstate(state)
        self._outport.send(mido.Message.from_bytes([0x90, note, value]))

    def set_strip_rgb_state(self, channel, state=1):
        note = strip_select_notes[channel]
        value = getvalue_fromstate(state)
        self._outport.send(mido.Message.from_bytes([0x90, note, value]))

    def set_all_buttonleds_off(self):
        """Turns off all the leds."""
        for button in _ButtonList:
            if button.led_type == 1:
                self.set_any_led(button, state=0)

    def set_strip_scribblemode(self, channel, mode: int = ScribbleStripMode.Default):
        ar = self._sysexhdr + [0x13, channel, mode] + [0xf7]
        self._outport.send(mido.Message.from_bytes(ar))

    def set_strip_scribbletext(self, channel, text, line=0, alignment=0):
        asciitext = [ord(x) for x in text]
        ar = self._sysexhdr + [0x12, channel, line, alignment] + asciitext + [0xf7]
        self._outport.send(mido.Message.from_bytes(ar))

    def set_strip_scribbletext_spanon_chan(self, channel, line, text, col_num=8):
        # strings = [line.strip() for line in text]
        words = text.split()
        lineno = line
        chan = channel
        tot = 0
        sline = ""
        self.set_strip_scribblemode(chan, ScribbleStripMode.Menu)
        for word in words:
            tot += len(word) + 1
            sline += word + ' '
            # print(f"sline={sline}")
            if tot > col_num:
                self.set_strip_scribbletext(chan, sline, lineno, 1)
                chan += 1
                sline = ""
                self.set_strip_scribblemode(chan, ScribbleStripMode.Menu)

    def clear_all_scribbletext(self):
        for line in range(7):
            for chan in range(self.channel_number):
                self.set_strip_scribbletext(chan, "", line)

    def on_encoder(self, channel, increment, pushed=False):
        """
        Session Navigator Encoder is rotated
        """
        val = self.strips[self.selected_channel].fader_value
        newval = clamp(val + increment, 0, self.max_fader_value)
        print(f"Session value: {increment} current={newval}")
        if pushed:
            newval = round(self.max_fader_value / 3)
        self.set_strip_fader(channel, newval)
        self.strips[self.selected_channel].fader_value = newval
        self.on_strip_fadermove(channel, newval)

    def on_panparam(self, channel, increment, pushed=False):
        """
        Pan/Param rotary is rotated
        """
        val = self.strips[self.selected_channel].panparam_value
        newval = clamp(val + increment, 0, self.max_rotation_value)
        if pushed:
            newval = round(self.max_rotation_value / 3)
        print(f"Pan/Param value: {increment} current={newval}")
        self.set_valuebarmode(self.selected_channel, ValueBarMode.Spread)
        self.set_valuebar(channel, newval)
        self.strips[self.selected_channel].panparam_value = newval

    def on_strip_mute(self, channel: int, pushed: bool):
        """
        Strip mute pushed or released
        """
        print(f"Mute: {channel} {pushed}")
        if pushed:
            self.strips[channel].muted = not self.strips[channel].muted
            self.set_strip_led_mute(channel, self.strips[channel].muted)

    def on_strip_solo(self, channel: int, pushed: bool):
        """
        Strip solo pushed or released
        """
        print(f"Solo: {channel} {pushed}")
        if pushed:
            self.strips[channel].soloed = not self.strips[channel].soloed
            self.set_strip_led_solo(channel, self.strips[channel].soloed)

    def on_strip_fadertouch(self, channel: int, pushed: bool):
        # print(f"Fader: {channel} {'touched' if pushed else 'released'}")
        if pushed:
            # self.set_strip_rgb_select(channel, 0xffffff)
            self.set_peak_meter(channel, 0x7f * 4)
            self.set_strip_rgb_state(channel, 1)
        else:
            if channel != self.selected_channel:
                self.set_strip_rgb_state(channel, 0)
            # self.set_strip_rgb_select(channel, 0x111100)

    def set_peak_meter(self, channel, value):
        """
        Real time metering.
        It is fading.
        Value is standardised to 0-1023 rather than 0-127
        (note) Value bar mode (0: normal, 1: bipolar, 2: fill, 3: spread, 4: off )
        """
        val = round(value / 4)
        if channel <= 7:
            self._outport.send(mido.Message('aftertouch', value=val, channel=channel))
        else:  # Send a program change, not aftertouch here for 8-15
            self._outport.send(mido.Message('program_change', program=val, channel=channel - 8))

    def set_reduction_meter(self, channel, value):
        val = 128 - int(value / 8) - 1
        # print("val=", val)
        if channel <= 7:
            self._outport.send(mido.Message('aftertouch', value=val, channel=channel + 8))
        else:
            # Send a program change, not aftertouch here for 8-15
            self._outport.send(mido.Message('program_change', program=val, channel=channel))

    def set_valuebarmode(self, channel, value):
        if channel <= 7:
            self._outport.send(mido.Message('control_change', channel=0,
                                            control=0x30 + channel + 0x08,
                                            value=value))
        else:
            self._outport.send(mido.Message('control_change', channel=0,
                                            control=0x40 + channel - 8 + 0x08,
                                            value=value))

    def set_valuebar(self, channel, value):
        # self.outport.send(mido.Message('control_change', channel=channel, control=0x10, value=value))
        if channel <= 7:
            self._outport.send(mido.Message('control_change', channel=0,
                                            control=0x30 + channel,
                                            value=value))
        else:
            self._outport.send(mido.Message('control_change', channel=0,
                                            control=0x40 + channel - 8,
                                            value=value))

    def on_strip_fadermove(self, channel, value):
        self.strips[channel].fader_value = value
        # print(f"Fader #: {channel} {value}")
        val = round(value * 100 / 1023)
        self.set_strip_scribbletext(channel=channel, text=str(val) + "%", line=0)
        self.set_reduction_meter(channel, value)
        if value == 0:
            self.set_strip_rgb_select(channel, 0xa00000, state=2)
        elif value == self.max_fader_value:
            self.set_strip_rgb_select(channel, 0x00c000, state=2)
        elif value < self.max_fader_value / 4:
            self.set_strip_rgb_select(channel, 0xa00000)
        elif value < self.max_fader_value / 2:
            self.set_strip_rgb_select(channel, 0xbb9900)
        elif value < self.max_fader_value - 120:
            self.set_strip_rgb_select(channel, 0x0000dd)
        elif value < self.max_fader_value - 8:
            self.set_strip_rgb_select(channel, 0x00c000)

    def on_strip_select(self, channel: int, pushed: bool = True):
        """
        Strip selected : turn off the other select buttons
        """
        if not pushed:
            return
        channel = clamp(channel, 0, self.channel_number - 1)
        self.selected_channel = channel
        val: int = round(random() * 0xffffff)
        for chan in range(self.channel_number):
            if chan == channel:
                self.set_strip_rgb_select(chan, val, 1)
                self.set_strip_fader(chan, self.strips[chan].fader_value)
            else:
                self.set_strip_rgb_state(chan, 0)
                self.set_strip_fader(chan, self.strips[chan].fader_value)

    def set_defaults(self):
        self.clear_all_scribbletext()
        for chan in range(self.channel_number):
            self.set_strip_scribblemode(chan, ScribbleStripMode.DefaultTextMetering)
            # self.set_strip_scribbletext(text='chan= ' + str(chan), channel=chan, line=2)
            self.set_strip_scribbletext(text=str(chan), channel=chan, line=1)
            self.set_strip_scribbletext(chan, text="chan", line=2)
            self.set_strip_rgb_state(chan, 0)
            self.solo_clear()
            self.mute_clear()

    def on_fadermode_group(self, button, pushed):
        modes = [ScribbleStripMode.Menu,
                 ScribbleStripMode.SmallText,
                 ScribbleStripMode.AlternativeTextMetering,
                 ScribbleStripMode.MixedTextMetering]
        i = button.group_index()
        for chan in range(self.channel_number):
            self.set_strip_scribblemode(chan, modes[i])
        self.toggle_unique_in_group(button)

    def toggle_unique_in_group(self, button):
        """Set this in Button class with midi"""
        button.toggled = True
        self.set_any_led(button, 1)
        for b in button.get_buttons_from_group():
            if b != button:
                b.toggled = False
                self.set_any_led(b, 0)

    def on_session_navigator_group(self, button, pushed):
        # self.set_any_led(button, 1 if pushed else 0)
        demos = [demo_set_explanations, demo_rgb1, demo_fader1, demo_reinit]
        self.toggle_unique_in_group(button)
        if not pushed:
            return
        index = button.group_index()
        demo = demos[index]
        self.set_defaults()
        demo(self)

    def on_shift_select(self, button, pushed):
        """Right shift is toggable, left shift is to be maintained pushed while selecting another function"""
        if button.name == "ShiftL":
            self.shiftL = pushed
            self.set_any_led(button, 1 if self.shiftL else 0)
        elif button.name == "ShiftR":
            if pushed:
                self.shiftR = not self.shiftR
                self.set_any_led(button, 1 if self.shiftR else 0)


class FaderPort8(FaderPort16):
    """
    Class derived from the FaderPort16 with port name, midi header, etc. defaulted to
    values specific to the FaderPort8
    """

    def __init__(self):
        super().__init__()
        self._sysexhdr = [0xf0, 0x00, 0x01, 0x06, 0x02]
        self.channel_number = 8
        self.port_name_starts_with = 'PreSonus FP8'


def demo_rgb1(fp):
    from itertools import cycle
    iter_ = cycle([0x00, 0x22ff, 0x4400ff, 0x66ff44, 0x880099])
    for loop in range(100):
        for chan in range(16):
            val = next(iter_)
            fp.set_strip_rgb_select(chan, val, 1)
        time.sleep(0.05)


def demo_fader1(fp):
    iter_ = cycle([0, 64, 128, 192, 320, 512, 900, 1023,
                   700, 600, 500, 400, 300, 200, 100, 50, 12])
    for loop in range(32):
        for chan in range(16):
            val = next(iter_)
            fp.set_strip_fader(chan, val)
            if val == fp.max_fader_value:
                fp.set_strip_led_mute(chan, 1)
            else:
                fp.set_strip_led_mute(chan, 0)
            if val < 64:
                fp.set_strip_led_solo(chan, 1)
            else:
                fp.set_strip_led_solo(chan, 0)
        time.sleep(0.5)


def demo_reinit(fp):
    fp.set_defaults()


class DemoFaderPort8(FaderPort8):
    pass


def demo_set_explanations(fp):
    fp.clear_all_scribbletext()
    line = 0
    text = "Press the buttons [Audio-All] to set the faders."
    fp.set_strip_scribbletext_spanon_chan(0, line, text)
    text = "A channel strip can be selected"
    line += 1
    fp.set_strip_scribbletext_spanon_chan(0, line, text)
    text = "Touching a fader makes its vu-meter reach 100%."
    line += 1
    fp.set_strip_scribbletext_spanon_chan(0, line, text)
    text = "Select a channel with Prev/Next and increase/decrease the value with the Session Encoder."
    line += 1
    fp.set_strip_scribbletext_spanon_chan(0, line, text)
    text = "Change the scribble display mode with the Track-Pan buttons"
    line += 1
    fp.set_strip_scribbletext_spanon_chan(0, line, text)
    text = "With Pan/Param, set the valuebar(panning) value."
    line = 1
    fp.set_strip_scribbletext_spanon_chan(11, line, text)
    text = "Mute/Solo buttons can be toggled."
    text = "Press the Play/Pause button to start or stop the selected demo."
    line = 5
    fp.set_strip_scribbletext_spanon_chan(11, line, text)
    # scroll the text trough each scribble-text
    pass


def demo_faderport16():
    with FaderPort16() as fp:
        for loop in range(0, 1):
            for chan in range(0, fp.channel_number):
                val = int(random() * 1023)
                fp.set_strip_fader(chan, val)
            time.sleep(2)

        fp.set_defaults()
        demo_set_explanations(fp)
        channel = int(random() * fp.channel_number)
        fp.set_strip_fader(channel, round(1023 * random()))
        fp.selected_channel = channel
        fp.on_strip_select(channel)

        while not fp.end_demo:
            time.sleep(1)


# Imports do not execute the demo code
if __name__ == "__main__":
    demo_faderport16()
