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

    def key_press(self):
        self.cola.put_nowait(KeyEvent(KEY_PRESSED))

    def run(self):
        print('Monitor on')
        if self.keyboardListener is None:
            self.keyboardListener = xinterface.Interface(self.key_press)
        self.keyboardListener.start()
        while True:
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

    def stop(self):
        print('Monitor off')
        if self.keyboardListener is not None:
            self.keyboardListener.stop()
            self.keyboardListener = None


if __name__ == '__main__':
    km = KeyboardMonitor(1)
    km.start()
    time.sleep(2)
    km.set_monitor_on()
    time.sleep(20)
    km.set_monitor_off()
    time.sleep(10)
    km.set_monitor_on()
    time.sleep(5)
