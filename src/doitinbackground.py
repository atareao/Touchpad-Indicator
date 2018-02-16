#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of slimbooktouchpad
#
# Copyright (C) 2016-2018 Lorenzo Carbonell
# lorenzo.carbonell.cerezo@gmail.com
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

from gi.repository import GObject
from idleobject import IdleObject
from threading import Thread
import subprocess
import os
import shlex


class DoItInBackground(IdleObject, Thread):
    __gsignals__ = {
        'started': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
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
        self.printer.feed(('$ %s\n\r' % (command)).encode())
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
                self.printer.feed(stdout_line.encode())
            return_code = po.wait()
            if command.startswith('add-apt-repository') and\
                    answer.find('OK') == -1:
                        self.ok = False
            if return_code:
                output = 'Error: %s\n\r' % (return_code)
                output = output + po.stderr.read().replace('\n', '\n\r') +\
                    '\n\r'
                self.printer.feed(output.encode())
                self.ok = False
        except OSError as e:
            print('Execution failed:', e)
            self.ok = False

    def stop(self, *args):
        self.stopit = True

    def run(self):
        self.emit('started')
        for index, command in enumerate(self.commands):
            if self.stopit is True:
                break
            self.execute(command)
            self.emit('done_one', command)
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
