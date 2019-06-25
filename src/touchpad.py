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

import re
import shlex
import subprocess
import time


TOUCHPADS = ['touchpad', 'glidepoint', 'fingersensingpad', 'bcm5974',
             'dll0665', 'dll05e3', 'cyps/2', 'alpsps/2', 'imexps/2',
             'synaptics', 'elantech', 'imps/2', 'dll07a8', 'dll077c']

SYNAPTICS = 0
LIBINPUT = 1
EVDEV = 2
UNRECOGNISED = -1

TWO_FINGERS = 0
EDGE = 1
CIRCULAR = 2

MINIMUM_TIME = 0.05


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
        return UNRECOGNISED

    def _get_type(self, id):
        test_str = run('xinput --list-props %s' % (id)).lower()
        return self._get_type_from_string(test_str)

    def get_driver(self):
        """
        Return touchpad's driver
        """
        ids = self._get_ids()
        if ids:
            return self._get_type(ids[0])
        return UNRECOGNISED

    def has_tapping(self):
        ids = self._get_ids()
        for id in ids:
            if not self._has_tapping(id):
                return False
        return True

    def _has_tapping(self, id):
        test_str = run('xinput --list-props %s' % (id)).lower()
        regex = r'tapping\s*enabled\s*\(\d*\):.*'
        matches = re.search(regex, test_str)
        return matches is not None

    def get_capabilities(self):
        ids = self._get_ids()
        if len(ids) > 0:
            return self._get_capabilities(ids[0])
        return {'phisical-left_button': False,
                'phisical-middle_button': False,
                'phisical-right_button': False,
                'two-finger-detection': False,
                'three-finger-detection': False,
                'vertical-resolution-configurable': False,
                'horizontal-resolution-configurable': False}

    def _get_capabilities(self, id):
        ans = {'phisical-left_button': False,
               'phisical-middle_button': False,
               'phisical-right_button': False,
               'two-finger-detection': False,
               'three-finger-detection': False,
               'vertical-resolution-configurable': False,
               'horizontal-resolution-configurable': False}
        test_str = run('xinput --list-props %s' % (id)).lower()
        regex = r'synaptics\scapabilities\s\(\d*\):\s*(\d),\s*(\d),\s*(\d),\s*(\d),\s*(\d),\s*(\d),\s*(\d)'
        values = re.findall(regex, test_str)
        if len(values) > 0:
            ans['phisical-left-button'] = (values[0][0] == '1')
            ans['phisical-middle-button'] = (values[0][1] == '1')
            ans['phisical-right-button'] = (values[0][2] == '1')
            ans['two-finger-detection'] = (values[0][3] == '1')
            ans['three-finger-detection'] = (values[0][4] == '1')
            ans['vertical-resolution-configurable'] = (values[0][5] == '1')
            ans['horizontal-resolution-configurable'] = (values[0][6] == '1')
        return ans

    def get_tap_configuration(self):
        ids = self._get_ids()
        if len(ids) > 0:
            return self._get_tap_configuration(ids[0])
        return {'phisical-left-button': 0,
                'phisical-middle-button': 0,
                'phisical-right-button': 0,
                'two-finger-detection': 0,
                'three-finger-detection': 0,
                'vertical-resolution-configurable': 0,
                'horizontal-resolution-configurable': 0}

    def _get_tap_configuration(self, id):
        """0 - disable, 1 - left button, 2 - middle button, 3 - right button"""
        ans = {'right-top-corner': 0,
               'right-bottom-corner': 0,
               'left-top-corner': 0,
               'left-bottom-corner': 0,
               'one-finger-tap': 0,
               'two-finger-tap': 0,
               'three-finger-tap': 0}
        test_str = run('xinput --list-props %s' % (id)).lower()
        regex = r'synaptics\s*tap\s*action\s*\(\d*\):\s*(\d),\s*(\d),\s*(\d),\s*(\d),\s*(\d),\s*(\d),\s*(\d)'
        values = re.findall(regex, test_str)
        if len(values) > 0:
            ans['right-top-corner'] = int(values[0][0])
            ans['right-bottom-corner'] = int(values[0][1])
            ans['left-top-corner'] = int(values[0][2])
            ans['left-bottom-corner'] = int(values[0][3])
            ans['one-finger-tap'] = int(values[0][4])
            ans['two-finger-tap'] = int(values[0][5])
            ans['three-finger-tap'] = int(values[0][6])
        return ans

    def _set_tap_configuration(self, id, configuration):
        test_str = run('xinput --list-props %s' % (id)).lower()
        regex = r'synaptics\s*tap\s*action\s*\((\d*)\):\s*\d,\s*\d,\s*\d,\s*\d,\s*\d,\s*\d,\s*\d'
        values = re.findall(regex, test_str.lower())
        if len(values) > 0:
            prop = values[0]
            run('\
xinput --set-prop {0} {1} {2}, {3}, {4}, {5}, {6}, {7}, {8}'.format(id, prop,
                configuration['right-top-corner'],  # 2
                configuration['right-bottom-corner'],  # 3
                configuration['left-top-corner'],  # 4
                configuration['left-bottom-corner'],  # 5
                configuration['one-finger-tap'],  # 6
                configuration['two-finger-tap'],  # 7
                configuration['three-finger-tap']))
            return True
        return False

    def set_tap_configuration(self, configuration):
        ans = True
        for id in self._get_ids():
            ans = self._set_tap_configuration(id, configuration)
        return ans

    def get_tapping(self):
        ids = self._get_ids()
        if len(ids) > 0:
            return self._get_tapping(ids[0])
        return False

    def _get_tapping(self, id):
        test_str = run('xinput --list-props %s' % (id)).lower()
        regex = r'tapping\s*enabled\s*\(\d*\):\s*(.*)'
        matches = re.search(regex, test_str)
        if matches is not None:
            return matches.group(1) == '1'
        return False

    def _set_tapping(self, id, tapping):
        test_str = run('xinput --list-props %s' % (id)).lower()
        regex = r'tapping\s*enabled\s*\((\d*)\):\s*(.*)'
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

    def _can_two_finger_scrolling(self, id):
        test_str = run('xinput --list-props %s' % (id)).lower()
        regex = r'scroll\s*methods\s*available\s*\(\d*\):\s*(\d),\s*\d,\s*\d'
        matches = re.search(regex, test_str)
        if matches is not None:
            if matches.group(1) == '1':
                return True
        return False

    def set_two_finger_scrolling(self, on=True):
        for id in self._get_ids():
            self._set_two_finger_scrolling(id, on)

    def _set_two_finger_scrolling(self, id, on=True):
        test_str = run('xinput --list-props %s' % (id)).lower()
        touchpad_type = self._get_type(id)
        if touchpad_type == LIBINPUT:
            regex = r'scroll\s*method\s*enabled\s*\((\d*)\)'
        elif touchpad_type == SYNAPTICS:
            regex = r'two-finger\s*scrolling\s*\((\d*)\)'
        else:
            return
        matches = re.search(regex, test_str)
        if matches is not None:
            if touchpad_type == LIBINPUT:
                if on is True:
                    run('xinput --set-prop %s %s 1, 0, 0' % (
                        id, matches.group(1)))
                else:
                    run('xinput --set-prop %s %s 0, 0, 0' % (
                        id, matches.group(1)))
            elif touchpad_type == SYNAPTICS:
                if on is True:
                    run('xinput --set-prop %s %s 1, 1' % (
                        id, matches.group(1)))
                else:
                    run('xinput --set-prop %s %s 0, 0' % (id,
                                                          matches.group(1)))

    def can_two_finger_scrolling(self):
        for id in self._get_ids():
            if self._can_two_finger_scrolling(id) is False:
                return False
        return True

    def _can_edge_scrolling(self, id):
        test_str = run('xinput --list-props %s' % (id)).lower()
        regex = r'scroll\s*methods\s*available\s*\(\d*\):\s*\d,\s*(\d),\s*\d'
        matches = re.search(regex, test_str)
        if matches is not None:
            if matches.group(1) == '1':
                return True
        return False

    def _set_edge_scrolling(self, id, on=True):
        test_str = run('xinput --list-props %s' % (id)).lower()
        touchpad_type = self._get_type(id)
        if touchpad_type == LIBINPUT:
            regex = r'scroll\s*method\s*enabled\s*\((\d*)\)'
        elif touchpad_type == SYNAPTICS:
            regex = r'edge\s*scrolling\s*\((\d*)\)'
        else:
            return
        matches = re.search(regex, test_str)
        if matches is not None:
            if touchpad_type == LIBINPUT:
                if on is True:
                    run('xinput --set-prop %s %s 0, 1, 0' % (
                        id, matches.group(1)))
                else:
                    run('xinput --set-prop %s %s 0, 0, 0' % (
                        id, matches.group(1)))
            elif touchpad_type == SYNAPTICS:
                if on is True:
                    run('xinput --set-prop %s %s 1, 1, 0' % (
                        id, matches.group(1)))
                else:
                    run('xinput --set-prop %s %s 0, 0, 0' % (
                        id, matches.group(1)))

    def set_edge_scrolling(self, on=True):
        for id in self._get_ids():
            self._set_edge_scrolling(id, on)

    def can_edge_scrolling(self):
        for id in self._get_ids():
            if self._can_edge_scrolling(id) is False:
                return False
        return True

    def _set_circular_scrolling(self, id, on=True):
        test_str = run('xinput --list-props %s' % (id)).lower()
        touchpad_type = self._get_type(id)
        if touchpad_type == SYNAPTICS:
            regex = r'circular\s*scrolling\s*\((\d*)\):\s*\d'
        else:
            return
        matches = re.search(regex, test_str)
        if matches is not None:
            run('xinput --set-prop %s %s %s' % (
                id, matches.group(1), 1 if on is True else 0))

    def set_circular_scrolling(self, on=True):
        for id in self._get_ids():
            self._set_circular_scrolling(id, on)

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
        elif type_of_touchpad == EVDEV or type_of_touchpad == SYNAPTICS:
            regex = \
                r'device\s*accel\s*constant\s*deceleration\s*\(\d*\):\s*(.*)'
        else:
            return 0.0
        matches = re.search(regex, test_str)
        if matches is not None:
            if type_of_touchpad == EVDEV or type_of_touchpad == SYNAPTICS:
                return float(matches.group(1)) - 1.0
            return float(matches.group(1))
        return 0.0

    def _set_speed(self, id, speed):
        test_str = run('xinput --list-props %s' % (id)).lower()
        type_of_touchpad = self._get_type_from_string(test_str)
        if type_of_touchpad == LIBINPUT:
            regex = r'libinput\s*accel\s*speed\s*\((\d*)\):\s*.*'
        elif type_of_touchpad == EVDEV or type_of_touchpad == SYNAPTICS:
            speed = speed + 1.0
            if speed <= 0:
                speed = 0.1
            regex = \
                r'device\s*accel\s*constant\s*deceleration\s*\((\d*)\):\s*.*'
        else:
            return
        matches = re.search(regex, test_str)
        if matches is not None:
            run('xinput --set-prop %s %s %s' % (
                id, matches.group(1), speed))

    def set_speed(self, speed):
        for id in self._get_ids():
            self._set_speed(id, speed)

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
    '''
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
    print(tp.has_tapping())
    '''
    print('----', tp.can_two_finger_scrolling())
    print('----', tp.can_edge_scrolling())
    exit(0)
