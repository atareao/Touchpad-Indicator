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

import threading
import queue
import collections
import CONSTANTS


class Service(threading.Thread):

    def __init__(self, interface):
        threading.Thread.__init__(self)
        self.daemon = True
        self.name = 'Listener service'
        self.interface = interface
        self.queue = queue.Queue()
        self.input_stack = collections.deque(maxlen=128)

        self.clear_stack = {CONSTANTS.XK.XK_Left, CONSTANTS.XK.XK_Right,
                            CONSTANTS.XK.XK_Up, CONSTANTS.XK.XK_Down,
                            CONSTANTS.XK.XK_Home, CONSTANTS.XK.XK_Page_Up,
                            CONSTANTS.XK.XK_Page_Down, CONSTANTS.XK.XK_End}
        self.service_running = False

    def enqueue(self, method, *args):
        self.queue.put_nowait((method, args))

    def run(self):
        while True:
            method, args = self.queue.get()
            if method is None:
                break
            try:
                method(*args)
            except Exception as exc:
                print("Error in the service main loop\n", exc)
            self.queue.task_done()

    def stop(self):
        self.enqueue(None)

    def listener(self, keypress, keysym, raw_key, modifiers, window_class,
                 window_title):
        self.enqueue(self.update_window_info, window_class, window_title)
        self.enqueue(self.handle_event, keypress, keysym, raw_key, modifiers)

    def update_window_info(self, window_class, window_title):
        self.window_class = window_class
        self.window_title = window_title

    def handle_event(self, keypress, keysym, raw_key, modifiers):
        if keypress:
            self.interface.emit_event(keypress, keysym, raw_key, modifiers)
