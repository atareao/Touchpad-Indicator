#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# do_itÇ_afeter.py
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


from threading import Thread
import time


class DoItAfter(Thread):
    def __init__(self, callback, elapsed_time):
        Thread.__init__(self)
        self.daemon = True
        self.callback = callback
        self.elapsed_time = elapsed_time
        self.working = False
        self.stopit = False

    def run(self):
        self.working = True
        self.start_time = time.time()
        while(1):
            time.sleep(0.2)
            if self.stopit is True:
                return
            if time.time() > self.start_time + self.elapsed_time:
                self.callback()
                self.working = False
                return

    def stop(self):
        self.stopit = True

    def increase(self):
        self.start_time += 0.2

    def is_working(self):
        return self.working


if __name__ == '__main__':
    def callback():
        print('test')
    dia = DoItAfter(callback, 2)
    dia.start()
    dia.increase()
    time.sleep(5)
