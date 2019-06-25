#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of Touchpad-Indicator
#
# Copyright (C) 2010-2019 Lorenzo Carbonell<lorenzo.carbonell.cerezo@gmail.com>
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
import evdev
from evdev import ecodes
import selectors
from selectors import DefaultSelector, EVENT_READ
import time

KEY_PRESSED = 1
KEY_RELEASED = 0
KEY_NONE = -1

ignore_key_codes = [ecodes.KEY_LEFTCTRL, ecodes.KEY_LEFTSHIFT,
                    ecodes.KEY_RIGHTSHIFT, ecodes.KEY_LEFTALT,
                    ecodes.KEY_RIGHTCTRL, ecodes.KEY_RIGHTALT,
                    ecodes.KEY_LEFTMETA, ecodes.KEY_HOME, ecodes.KEY_UP,
                    ecodes.KEY_PAGEUP, ecodes.KEY_LEFT, ecodes.KEY_RIGHT,
                    ecodes.KEY_END, ecodes.KEY_DOWN, ecodes.KEY_PAGEDOWN,
                    ecodes.KEY_MUTE, ecodes.KEY_VOLUMEDOWN,
                    ecodes.KEY_VOLUMEUP, ecodes.KEY_PAUSE]

def get_keyboards():
    keyboards = []
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    for device in devices:
        evDevDevice = evdev.InputDevice(device)
        caps = evDevDevice.capabilities()
        if ecodes.EV_KEY in caps and ecodes.KEY_ESC in caps[ecodes.EV_KEY]:
            keyboards.append(evDevDevice)
    return keyboards

class KeyboardMonitor(Thread, GObject.GObject):
    __gsignals__ = {
        'key_pressed': (GObject.SIGNAL_RUN_FIRST, None, ()),
        'key_released': (GObject.SIGNAL_RUN_FIRST, None, ()),
    }

    def __init__(self, elapsed_time):
        Thread.__init__(self)
        GObject.GObject.__init__(self)
        self.daemon = True

        self.elapsed_time = float(elapsed_time)/1000.0
        self.last_keypress = 0
        self.last_emited = ''

        self.work = True
        self.on = False

    def update_last_keypress(self, event):
        if event.type == ecodes.EV_KEY and not event.code in ignore_key_codes:
            self.last_keypress = event.timestamp()

    def run(self):
        selector = selectors.DefaultSelector()
        for keyboard in get_keyboards():
            selector.register(keyboard, selectors.EVENT_READ)
        while self.work:
            if self.last_emited != 'key_released' and self.on:
                self.emit('key_released')
                self.last_emited = 'key_released'
            for key, mask in selector.select():
                device = key.fileobj
                while True: # we will stay in this loop until we can enable the  touchpad again
                    try:
                        for event in device.read():
                            self.update_last_keypress(event)
                    except BlockingIOError: # this will be raised by device.     read() if there is no more event to read
                        pass
                    timeToSleep = (self.last_keypress + self.elapsed_time) - time.time()
                    if timeToSleep <= 0.005: # you can set this to 0, but that   may result in unnecessarily short (and imperceptible) sleep times.
                        # touchpad can be enabled again, so break loop.
                        break
                    else:
                        # disable touchpad and wait until we need to check next. disableTouchpad() takes care of only invoking xinput if necessary.
                        if self.last_emited != 'key_pressed' and self.on:
                            self.emit('key_pressed')
                            self.last_emited = 'key_pressed'
                        print(timeToSleep)
                        time.sleep(timeToSleep)

    def end(self):
        self.work = False

    def is_on(self):
        return self.on

    def set_on(self, on):
        self.on = on
