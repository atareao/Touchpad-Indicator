#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# touchpad.py
#
# Copyright (C) 2010,2011
# Lorenzo Carbonell Cerezo <lorenzo.carbonell.cerezo@gmail.com>
# Miguel Angel Santamaría Rogado <leibag@gmail.com>
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

import re
import shlex
import subprocess
import time


TOUCHPADS = ['touchpad', 'glidepoint', 'fingersensingpad', 'bcm5974',
             'dll0665', 'dll05e3', 'cyps/2', 'alpsps/2', 'imexps/2',
             'synaptics', 'elantech', 'imps/2']


def run(comando):
    args = shlex.split(comando)
    p = subprocess.Popen(args, bufsize=10000, stdout=subprocess.PIPE)
    valor = p.communicate()[0]
    return valor.decode('utf-8')


def search_touchpad(where):
    where = where.lower()
    for touchpad in TOUCHPADS:
        if where.find(touchpad) != -1:
            return True
    if where.find('ps/2 generic mouse') != -1:
        return True
    return False


class Touchpad(object):
    def __init__(self):
        # self.synclient = Synclient()
        pass

    def _get_all_ids(self):
        ids = []
        lines = run('xinput --list')
        for line in lines.split('\n'):
            if line.find('id=') != -1:
                line = line.strip()
                match = re.search('id=([0-9]+)', line)
                deviceId = str(match.group(1))
                ids.append(deviceId)
        return ids

    def _is_touchpad(self, id):
        comp = run(('xinput --list-props %s') % (id))
        return search_touchpad(comp)

    def is_there_touchpad(self):
        comp = run('xinput --list')
        return search_touchpad(comp)

    def _get_ids(self):
        ids = []
        for id in self._get_all_ids():
            if self._is_touchpad(id):
                ids.append(id)
        return ids

    def set_touchpad_enabled(self, id):
        run(('xinput set-prop %s "Device Enabled" 1') % id)

    def set_touchpad_disabled(self, id):
        run(('xinput set-prop %s "Device Enabled" 0') % id)

    def is_touchpad_enabled(self, id):
        lines = run('xinput --list-props %s' % id)
        for line in lines.split('\n'):
            if line.lower().find('device enabled') != -1:
                if line.split(':')[1].strip() == '1':
                    return True
        return False

    def disable_all_touchpads(self):
        for id in self._get_ids():
            self.set_touchpad_disabled(id)
            time.sleep(1)
        # self.synclient.set('TouchpadOff', '1')
        return not self.are_all_touchpad_enabled()

    def enable_all_touchpads(self):
        for id in self._get_ids():
            print('Enabling: %s' % (id))
            print(self.set_touchpad_enabled(id))
            time.sleep(1)
        return self.are_all_touchpad_enabled()

    def are_all_touchpad_enabled(self):
        ids = self._get_ids()
        if len(ids) > 0:
            for id in ids:
                if not self.is_touchpad_enabled(id):
                    return False
            return True
        return False

    def are_all_touchpad_disabled(self):
        ids = self._get_ids()
        if len(ids) > 0:
            for id in ids:
                if self.is_touchpad_enabled(id):
                    return False
            return True
        return False


if __name__ == '__main__':
    tp = Touchpad()
    print('Is there touchpad? %s' % tp.is_there_touchpad())
    print(tp._get_ids())
    print(tp.are_all_touchpad_enabled())
    print(tp.disable_all_touchpads())
    print('sleeping...')
    time.sleep(5)
    print(tp.are_all_touchpad_disabled())
    print(tp.enable_all_touchpads())
    exit(0)
