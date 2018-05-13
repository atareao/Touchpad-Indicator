#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of Touchpad-Indicator
#
# Copyright (C) 2010-2018 Lorenzo Carbonell<lorenzo.carbonell.cerezo@gmail.com>
# Copyright (C) 2010-2012 Miguel Angel Santamaría Rogado<leibag@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gi
try:
    gi.require_version('GObject', '2.0')
except Exception as e:
    print(e)
    exit(-1)
from gi.repository import GObject
from threading import Thread
import queue
import time
import xinterface

KEY_PRESSED = 1
KEY_RELEASED = 0
KEY_NONE = -1

ALT_L = 65513  # keycode: 64  The left-hand alt key
ALT_R = 65514  # keycode: 113  The right-hand alt key
BACKSPACE = 65288  # keycode: 22  backspace
CANCEL = 65387  # keycode: 110  break
CAPS_LOCK = 65549  # keycode: 66  CapsLock
CONTROL_L = 65507  # keycode: 37  The left-hand control key
CONTROL_R = 65508  # keycode: 109  The right-hand control key
DELETE = 65535  # keycode: 107  Delete
DOWN = 65364  # keycode: 104  ↓
END = 65367  # keycode: 103  end
ESCAPE = 65307  # keycode: 9  esc
EXECUTE = 65378  # keycode: 111  SysReq
F1 = 65470  # keycode: 67  Function key F1
F2 = 65471  # keycode: 68  Function key F2
F3 = 65472  # keycode: 69  Function key F3
F4 = 65473  # keycode: 70  Function key F4
F5 = 65474  # keycode: 71  Function key F5
F6 = 65475  # keycode: 72  Function key F6
F7 = 65476  # keycode: 73  Function key F7
F8 = 65477  # keycode: 74  Function key F8
F9 = 65478  # keycode: 75  Function key F9
F10 = 65479  # keycode: 76  Function key F10
F11 = 65480  # keycode: 77  Function key F11
F12 = 65481  # keycode: 96  Function key F12
HOME = 65360  # keycode: 97  home
INSERT = 65379  # keycode: 106  insert
LEFT = 65361  # keycode: 100  ←
LINEFEED = 106  # keycode: 54  Linefeed (control-J)
KP_0 = 65438  # keycode: 90  0 on the keypad
KP_1 = 65436  # keycode: 87  1 on the keypad
KP_2 = 65433  # keycode: 88  2 on the keypad
KP_3 = 65435  # keycode: 89  3 on the keypad
KP_4 = 65430  # keycode: 83  4 on the keypad
KP_5 = 65437  # keycode: 84  5 on the keypad
KP_6 = 65432  # keycode: 85  6 on the keypad
KP_7 = 65429  # keycode: 79  7 on the keypad
KP_8 = 65431  # keycode: 80  8 on the keypad
KP_9 = 65434  # keycode: 81  9 on the keypad
KP_ADD = 65451  # keycode: 86  + on the keypad
KP_BEGIN = 65437  # keycode: 84  The center key (same key as 5) on the keypad
KP_DECIMAL = 65439  # keycode: 91  Decimal (.) on the keypad
KP_DELETE = 65439  # keycode: 91  delete on the keypad
KP_DIVIDE = 65455  # keycode: 112  / on the keypad
KP_DOWN = 65433  # keycode: 88  ↓ on the keypad
KP_END = 65436  # keycode: 87  end on the keypad
KP_ENTER = 65421  # keycode: 108  enter on the keypad
KP_HOME = 65429  # keycode: 79  home on the keypad
KP_INSERT = 65438  # keycode: 90  insert on the keypad
KP_LEFT = 65430  # keycode: 83  ← on the keypad
KP_MULTIPLY = 65450  # keycode: 63  × on the keypad
KP_NEXT = 65435  # keycode: 89  PageDown on the keypad
KP_PRIOR = 65434  # keycode: 81  PageUp on the keypad
KP_RIGHT = 65432  # keycode: 85  → on the keypad
KP_SUBTRACT = 65453  # keycode: 82  - on the keypad
KP_UP = 65431  # keycode: 80  ↑ on the keypad
NEXT = 65366  # keycode: 105  PageDown
NUM_LOCK = 65407  # keycode: 77  NumLock
PAUSE = 65299  # keycode: 110  pause
PRINT = 65377  # keycode: 111  PrintScrn
PRIOR = 65365  # keycode: 99  PageUp
RETURN = 65293  # keycode: 36  The enter key (control-M).
# The name Enter refers to a mouse-related event, not a keypress; see
# Section 54, “Events”
RIGHT = 65363  # keycode: 102  →
SCROLL_LOCK = 65300  # keycode: 78  ScrollLock
SHIFT_L = 65505  # keycode: 50  The left-hand shift key
SHIFT_R = 65506  # keycode: 62  The right-hand shift key
TAB = 65289  # keycode: 23  The tab key
UP = 65362  # keycode: 98  ↑
SUPER = 65515  # Super

NOTINCLUDED = [ALT_L,
               ALT_R,
               CANCEL,
               CAPS_LOCK,
               CONTROL_L,
               CONTROL_R,
               DOWN,
               END,
               ESCAPE,
               F1,
               F2,
               F3,
               F4,
               F5,
               F6,
               F7,
               F8,
               F9,
               F10,
               F11,
               F12,
               HOME,
               INSERT,
               LEFT,
               KP_ADD,
               KP_BEGIN,
               KP_DOWN,
               KP_END,
               KP_HOME,
               KP_INSERT,
               KP_LEFT,
               KP_NEXT,
               KP_PRIOR,
               KP_RIGHT,
               KP_UP,
               NEXT,
               NUM_LOCK,
               PAUSE,
               PRINT,
               PRIOR,
               RIGHT,
               SCROLL_LOCK,
               SHIFT_L,
               SHIFT_R,
               SUPER,
               UP]


class KeyEvent():
    def __init__(self, eventtype):
        self.eventtype = eventtype
        self.instant = time.time()


class KeyboardMonitor(Thread, GObject.GObject):
    __gsignals__ = {
        'key_pressed': (GObject.SIGNAL_RUN_FIRST, None, ()),
        'key_released': (GObject.SIGNAL_RUN_FIRST, None, ()),
    }

    def __init__(self, elapsed_time):
        Thread.__init__(self)
        GObject.GObject.__init__(self)
        self.daemon = True

        self.keyboardListener = xinterface.Interface(self.key_press)
        self.elapsed_time = elapsed_time / 1000.0
        self.cola = queue.Queue()
        self.last_event = None
        self.work = True
        self.on = False

    def key_press(self, keypress, keysym, raw_key, modifiers):
        if raw_key not in NOTINCLUDED and modifiers['<Control>'] is False and\
                modifiers['<Alt>'] is False and\
                modifiers['<Super>'] is False:
            self.cola.put_nowait(KeyEvent(KEY_PRESSED))

    def run(self):
        print('Monitor on')
        if self.keyboardListener is None:
            self.keyboardListener = xinterface.Interface(self.key_press)
        self.keyboardListener.start()
        while self.work:
            try:
                new_event = self.cola.get(True, self.elapsed_time)
                if new_event.eventtype in [KEY_PRESSED, KEY_RELEASED]:
                    if self.last_event is None or \
                            (self.last_event.eventtype == KEY_RELEASED and
                             new_event.eventtype == KEY_PRESSED) or\
                            (self.last_event.instant + self.elapsed_time <
                             new_event.instant):
                        if self.keyboardListener is not None:
                            if new_event.eventtype == KEY_PRESSED:
                                self.emit('key_pressed')
                            elif new_event.eventtype == KEY_RELEASED:
                                self.emit('key_released')
                    self.last_event = new_event
            except queue.Empty:
                if self.last_event is None or\
                        self.last_event.eventtype == KEY_RELEASED:
                    self.cola.put_nowait(KeyEvent(KEY_NONE))
                else:
                    self.cola.put_nowait(KeyEvent(KEY_RELEASED))

    def end(self):
        self.work = False

    def is_on(self):
        return self.on

    def set_on(self, on):
        self.on = on
        if on is True:
            print('Monitor on')
            if self.keyboardListener is None:
                self.keyboardListener = xinterface.Interface(self.key_press)
                self.keyboardListener.start()
            else:
                self.keyboardListener.stop()
                self.keyboardListener = None
                self.keyboardListener = xinterface.Interface(self.key_press)
                self.keyboardListener.start()
        else:
            print('Monitor off')
            if self.keyboardListener is not None:
                self.keyboardListener.stop()
                self.keyboardListener = None
