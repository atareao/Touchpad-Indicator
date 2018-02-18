#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# time_wather.py
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
import threading
import time


class TimeWatcher(threading.Thread):
    def __init__(self, time_interval, callback):
        threading.Thread.__init__(self)
        self.callback = callback
        self.daemon = True
        self.time_counter = 0
        self.last_time_event_happened = 0
        self.time_interval = time_interval
        self.can_run = True
        self.event = threading.Event()
        self.event.clear()

    def set_event_happened(self):
        self.last_time_event_happened = time.time()
        self.event.set()

    def stop(self):
        self.can_run = False

    def run(self):
        while self.can_run:
            time.sleep(0.1)
            self.event.wait()
            if time.time() - self.last_time_event_happened >\
                    self.time_interval:
                self.callback()
                self.event.clear()
