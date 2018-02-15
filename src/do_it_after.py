#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
