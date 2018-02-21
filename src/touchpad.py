#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# touchpad.py
#
# Copyright (C) 2010 - 2018
# Lorenzo Carbonell Cerezo <lorenzo.carbonell.cerezo@gmail.com>
# Copyright (C) 2010,2011
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

SYNAPTICS = 0
LIBINPUT = 1
EVDEV = 2

MINIMUM_TIME = 0.2


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
        pass

    def _get_all_ids(self):
        test_str = run('xinput --list').lower()
        regex = r'id=(\d*)'
        prog = re.compile(regex)
        return prog.findall(test_str)

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
        test_str = run('xinput --list-props %s' % (id)).lower()
        regex = r'device\s*enabled\s*\((\d*)\):\s*(\d)'
        matches = re.search(regex, test_str)
        if matches is not None:
            if matches.group(2) != '1':
                run(('xinput --set-prop %s %s 1') % (id, matches.group(1)))

    def set_touchpad_disabled(self, id):
        test_str = run('xinput --list-props %s' % (id)).lower()
        regex = r'device\s*enabled\s*\((\d*)\):\s*(\d)'
        matches = re.search(regex, test_str)
        if matches is not None:
            if matches.group(2) != '0':
                run(('xinput --set-prop %s %s 0') % (id, matches.group(1)))

    def is_touchpad_enabled(self, id):
        test_str = run('xinput --list-props %s' % (id)).lower()
        regex = r'device\s*enabled\s*\(\d*\):\s*(\d)'
        matches = re.search(regex, test_str)
        if matches is not None:
            return str(matches.group(1)) == '1'
        return False

    def disable_all_touchpads(self):
        for id in self._get_ids():
            self.set_touchpad_disabled(id)
            time.sleep(MINIMUM_TIME)
        return not self.are_all_touchpad_enabled()

    def enable_all_touchpads(self):
        for id in self._get_ids():
            self.set_touchpad_enabled(id)
            time.sleep(MINIMUM_TIME)
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

    def _get_type_from_string(self, test_str):
        regex = r'libinput'
        matches = re.search(regex, test_str)
        if matches is not None:
            if str(matches.group(0)) == 'libinput':
                return LIBINPUT
        else:
            regex = r'synaptics'
            matches = re.search(regex, test_str)
            if matches is not None:
                if str(matches.group(0)) == 'synaptics':
                    return SYNAPTICS
            else:
                regex = r'evdev'
                matches = re.search(regex, test_str)
                if matches is not None:
                    if str(matches.group(0)) == 'evdev':
                        return EVDEV
        return -1

    def _get_type(self, id):
        test_str = run('xinput --list-props %s' % (id)).lower()
        return self._get_type_from_string(test_str)

    def get_tapping(self):
        ids = self._get_ids()
        if len(ids) > 0:
            return self._get_tapping(ids[0])
        return False

    def _get_tapping(self, id):
        test_str = run('xinput --list-props %s' % (id)).lower()
        type_of_touchpad = self._get_type_from_string(test_str)
        if type_of_touchpad == LIBINPUT:
            regex = r'libinput\s*tapping\s*enabled\s*\(\d*\):\s*(.*)'
        elif type_of_touchpad == SYNAPTICS:
            regex = r'synaptics\s*tapping\s*enabled\s*\(\d*\):\s*(.*)'
        elif type_of_touchpad == EVDEV:
            regex = r'evdev\s*tapping\s*enabled\s*\(\d*\):\s*(.*)'
        else:
            return 0.0
        matches = re.search(regex, test_str)
        if matches is not None:
            return matches.group(1) == '1'
        return False

    def _set_tapping(self, id, tapping):
        test_str = run('xinput --list-props %s' % (id)).lower()
        type_of_touchpad = self._get_type_from_string(test_str)
        if type_of_touchpad == LIBINPUT:
            regex = r'libinput\s*tapping\s*enabled\s*\((\d*)\):\s*(.*)'
        elif type_of_touchpad == SYNAPTICS:
            regex = r'synaptics\s*tapping\s*enabled\s*\((\d*)\):\s*(.*)'
        elif type_of_touchpad == EVDEV:
            regex = r'evdev\s*tapping\s*enabled\s*\((\d*)\):\s*(.*)'
        else:
            return
        matches = re.search(regex, test_str)
        if matches is not None:
            print(matches.group(1), matches.group(2))
            if tapping is True and matches.group(2) == '1':
                return
            elif tapping is False and matches.group(2) == '0':
                return
            else:
                if tapping is True:
                    run(('xinput --set-prop %s %s 1') % (id, matches.group(1)))
                else:
                    run(('xinput --set-prop %s %s 0') % (id, matches.group(1)))

    def set_tapping(self, tapping):
        for id in self._get_ids():
            self._set_tapping(id, tapping)

    def get_speed(self):
        ids = self._get_ids()
        if len(ids) > 0:
            return self._get_speed(ids[0])
        return 0.0

    def _get_speed(self, id):
        test_str = run('xinput --list-props %s' % (id)).lower()
        type_of_touchpad = self._get_type_from_string(test_str)
        if type_of_touchpad == LIBINPUT:
            regex = r'libinput\s*accel\s*speed\s*\(\d*\):\s*(.*)'
        elif type_of_touchpad == SYNAPTICS:
            regex = r'synaptics\s*accel\s*speed\s*\(\d*\):\s*(.*)'
        elif type_of_touchpad == EVDEV:
            regex = r'evdev\s*accel\s*speed\s*\(\d*\):\s*(.*)'
        else:
            return 0.0
        matches = re.search(regex, test_str)
        if matches is not None:
            return float(matches.group(1))
        return 0.0

    def _set_speed(self, id, speed):
        test_str = run('xinput --list-props %s' % (id)).lower()
        type_of_touchpad = self._get_type_from_string(test_str)
        if type_of_touchpad == LIBINPUT:
            regex = r'libinput\s*accel\s*speed\s*\((\d*)\):\s*.*'
        elif type_of_touchpad == SYNAPTICS:
            regex = r'synaptics\s*accel\s*speed\s*\((\d*)\):\s*.*'
        elif type_of_touchpad == EVDEV:
            regex = r'evdev\s*accel\s*speed\s*\((\d*)\):\s*.*'
        else:
            return
        matches = re.search(regex, test_str)
        if matches is not None:
            run('xinput --set-prop %s %s %s' % (
                id, matches.group(1), speed))

    def set_speed(self, speed):
        for id in self._get_ids():
            self._set_speed(id, speed)

    def _set_default_speed(self, id):
        default_speed = self._get_default_speed(id)
        self._set_speed(id, default_speed)

    def set_default_speed(self):
        for id in self._get_ids():
            default_speed = self._get_default_speed(id)
            self._set_speed(id, default_speed)

    def _get_default_speed(self, id):
        test_str = run('xinput --list-props %s' % (id)).lower()
        type_of_touchpad = self._get_type_from_string(test_str)
        if type_of_touchpad == LIBINPUT:
            regex = r'libinput\s*accel\s*speed\s*default\s*\(\d*\):\s*(.*)'
        elif type_of_touchpad == SYNAPTICS:
            regex = r'synaptics\s*accel\s*speed\s*default\s*\(\d*\):\s*(.*)'
        elif type_of_touchpad == EVDEV:
            regex = r'evdev\s*accel\s*speed\s*default\s*\(\d*\):\s*(.*)'
        else:
            return 0.0
        matches = re.search(regex, test_str)
        if matches is not None:
            return float(matches.group(1))
        return 0.0

    def get_default_speed(self):
        ids = self._get_ids()
        if len(ids) > 0:
            return self._get_default_speed(ids[0])
        return 0.0

    def _is_natural_scrolling(self, id):
        test_str = run('xinput --list-props %s' % (id)).lower()
        type_of_touchpad = self._get_type_from_string(test_str)
        if type_of_touchpad == LIBINPUT:
            regex = r'natural\s*scrolling\s*enabled\s*\(\d*\):\s*(\d)'
        elif self._get_type(id) == SYNAPTICS:
            regex = r'synaptics\s*scrolling\s*distance\s*\(\d*\):\s*(-*)\d*'
        elif self._get_type(id) == EVDEV:
            regex = r'evdev\s*scrolling\s*distance\s*\(\d*\):\s*(-*)\d*'
        else:
            return False
        matches = re.search(regex, test_str)
        if matches is not None:
            if str(matches.group(1)) == '1':
                return True
        return False

    def set_natural_scrolling(self, id, natural_scrolling):
        test_str = run('xinput --list-props %s' % id).lower()
        type_of_touchpad = self._get_type_from_string(test_str)
        if type_of_touchpad == LIBINPUT:
            regex = r'natural\s*scrolling\s*enabled\s*\((\d*)\)'
            matches = re.search(regex, test_str)
            if matches is not None:
                if(natural_scrolling):
                    run('xinput --set-prop %s %s 1' % (
                        id, matches.group(1)))
                else:
                    run('xinput --set-prop %s %s 0' % (
                        id, matches.group(1)))
        elif self._get_type(id) == SYNAPTICS:
            regex = r'synaptics\s*scrolling\s*distance\s*\((\d*)\):\s*-*(\d*),\s*-*(\d*)'
            matches = re.search(regex, test_str)
            if matches is not None:
                if(natural_scrolling):
                    run('xinput --set-prop %s %s -%s, -%s' % (
                        id, matches.group(1), matches.group(2),
                        matches.group(3)))
                else:
                    run('xinput --set-prop %s %s %s, %s' % (
                        id, matches.group(1), matches.group(2),
                        matches.group(3)))
        elif self._get_type(id) == EVDEV:
            regex = r'evdev\s*scrolling\s*distance\s*\((\d*)\):\s*-*(\d*),\s*-*(\d*),\s*-*(\d*)'
            matches = re.search(regex, test_str)
            if matches is not None:
                if(natural_scrolling):
                    run('xinput --set-prop %s %s -%s, -%s, -%s' % (
                        id, matches.group(1), matches.group(2),
                        matches.group(3), matches.group(4)))
                else:
                    run('xinput --set-prop %s %s %s, %s, %s' % (
                        id, matches.group(1), matches.group(2),
                        matches.group(3), matches.group(4)))

    def set_natural_scrolling_for_all(self, natural_scrolling):
        ids = self._get_ids()
        if len(ids) > 0:
            for id in ids:
                self.set_natural_scrolling(id, natural_scrolling)

    def are_all_touchpad_natural_scrolling(self):
        ids = self._get_ids()
        if len(ids) > 0:
            for id in ids:
                if not self._is_natural_scrolling(id):
                    return False
            return True
        return False


if __name__ == '__main__':

    tp = Touchpad()
    print('Is there touchpad? %s' % tp.is_there_touchpad())
    print(tp._get_ids())
    print('Is touchpad enabled? %s' % tp.is_touchpad_enabled(12))
    print(tp.set_natural_scrolling_for_all(False))
    print('Natural srolling:', tp.are_all_touchpad_natural_scrolling())
    print(tp._get_type(12))
    print(tp._get_speed(12))
    print(tp.get_default_speed())
    print(tp.set_speed(0.3))
    # print(tp.set_default_speed())
    print('======')
    tp.disable_all_touchpads()
    print(tp.are_all_touchpad_disabled())
    print('======')
    tp.enable_all_touchpads()
    print(tp.are_all_touchpad_enabled())
    print(tp._set_tapping(12, True))
    print(tp.get_tapping())

    exit(0)
