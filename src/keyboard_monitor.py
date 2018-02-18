#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# keyboard_monitor.py
#
# Copyright (C) 2018
# Lorenzo Carbonell Cerezo <lorenzo.carbonell.cerezo@gmail.com>
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
from threading import Event
import time
from pynput import keyboard


class KeyboardMonitor(Thread, GObject.GObject):
    __gsignals__ = {
        'key_pressed': (GObject.SIGNAL_RUN_FIRST, None, ()),
        'key_released': (GObject.SIGNAL_RUN_FIRST, None, ()),
    }

    def __init__(self, elapsed_time):
        Thread.__init__(self)
        GObject.GObject.__init__(self)
        self.daemon = True
        self.keyboardListener = None
        self.elapsed_time = elapsed_time
        self.event = Event()
        self.is_pressing = False
        self.stopit = False

    def run(self):
        while(1):
            if self.event.wait() and self.stopit is False:
                if self.stopit:
                    return
                if self.start_time + self.elapsed_time < time.time():
                    print('callback')
                    self.event.clear()
                    self.is_pressing = False
                    self.emit('key_released')

    def on_press(self, key):
        if self.is_pressing is False:
            self.emit('key_pressed')
            self.event.clear()
            self.is_pressing = True

    def on_release(self, key):
        if self.start_time + 0.5 < time.time():
            print(key)
            self.event.set()
            self.start_time = time.time()
            return True

    def set_monitor_on(self):
        print('Monitor on')
        if self.keyboardListener is not None:
            self.set_monitor_off()
        self.keyboardListener = keyboard.Listener(on_press=self.on_press,
                                                  on_release=self.on_release)
        self.keyboardListener.start()
        self.start_time = 0

    def set_monitor_off(self):
        print('Monitor off')
        self.keyboardListener.stop()
        self.keyboardListener = None

    def stop(self):
        self.stopit = True

if __name__ == '__main__':
    km = KeyboardMonitor(None, .5)
    km.start()
    time.sleep(3)
    km.set_monitor_on()
    time.sleep(3)
    km.set_monitor_off()
    time.sleep(3)
    km.set_monitor_on()
    time.sleep(5)
