#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of Touchpad-Indicator
#
# Copyright (C) 2010-2019 Lorenzo Carbonell<lorenzo.carbonell.cerezo@gmail.com>
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
    gi.require_version('GLib', '2.0')
except Exception as e:
    print(e)
    exit(-1)
from gi.repository import GObject
from gi.repository import GLib
from idleobject import IdleObject
from threading import Thread
import subprocess
import os
import shlex
import time


class DoItInBackground(IdleObject, Thread):
    __gsignals__ = {
        'started': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (int, )),
        'ended': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (bool,)),
        'done_one': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE,
                     (str,)),
    }

    def __init__(self, printer, commands):
        IdleObject.__init__(self)
        Thread.__init__(self)
        self.printer = printer
        self.commands = commands
        self.stopit = False
        self.ok = True
        self.daemon = True

    def execute(self, command):
        GLib.idle_add(self.printer.feed, ('\n\r$ %s\n\r' % (command)).encode())
        env = os.environ.copy()
        answer = ''
        try:
            po = subprocess.Popen(shlex.split(command),
                                  shell=False,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  universal_newlines=True,
                                  env=env)
            for stdout_line in iter(po.stdout.readline, ''):
                answer += stdout_line
                stdout_line = stdout_line.replace('\n', '\n\r')
                GLib.idle_add(self.printer.feed, stdout_line.encode())
            return_code = po.wait()
            if return_code:
                output = 'Error: %s\n\r' % (return_code)
                output = output + po.stderr.read().replace('\n', '\n\r') +\
                    '\n\r'
                GLib.idle_add(self.printer.feed, output.encode())
                self.ok = False
        except OSError as e:
            print('Execution failed:', e)
            self.ok = False

    def stop(self, *args):
        self.stopit = True

    def run(self):
        self.emit('started', len(self.commands))
        for index, command in enumerate(self.commands):
            if self.stopit is True:
                break
            self.execute(command)
            print(command)
            self.emit('done_one', command)
            time.sleep(1)
        self.emit('ended', self.ok)


if __name__ == '__main__':
    from progreso import Progreso

    class testclass():
        def __init__(self):
            pass

        def feed(self, astring):
            print(astring.decode())

    tc = testclass()
    commands = ['ls', 'ls -la', 'ls']
    diib = DoItInBackground(tc, commands)
    progreso = Progreso('Adding new ppa', None, len(commands))
    diib.connect('done_one', progreso.increase)
    diib.connect('ended', progreso.close)
    progreso.connect('i-want-stop', diib.stop)
    diib.start()
