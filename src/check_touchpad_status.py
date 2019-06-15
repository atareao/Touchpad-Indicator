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

import dbus
from touchpad import Touchpad
from configurator import Configuration
import sys

if __name__ == '__main__':
    try:
        bus = dbus.SessionBus()
        touchpad_indicator_service = bus.get_object(
            'es.atareao.TouchpadIndicator', '/es/atareao/TouchpadIndicator')
        if len(sys.argv) > 1 and sys.argv[1] == 'resume':
            print(sys.argv)
            check_status_from_resume = \
                touchpad_indicator_service.get_dbus_method(
                    'check_status_from_resume', 'es.atareao.TouchpadIndicator')
            check_status_from_resume()
        else:
            check_status = touchpad_indicator_service.get_dbus_method(
                'check_status', 'es.atareao.TouchpadIndicator')
            check_status()
        print('Touchpad-Indicator is working')
    except dbus.exceptions.DBusException as argument:
        print(argument)
        touchpad = Touchpad()
        configuration = Configuration()
        touchpad_enabled = configuration.get('touchpad_enabled')
        touchpad_indicator_working = configuration.get('is_working')
        status = touchpad.are_all_touchpad_enabled()
        if touchpad_indicator_working:
            print('Touchpad-Indicator is working')
            if touchpad_enabled != status:
                if touchpad_enabled:
                    touchpad.enable_all_touchpads()
                else:
                    touchpad.disable_all_touchpads()
                newstatus = touchpad.are_all_touchpad_enabled()
                if status != newstatus:
                    configuration.set('touchpad_enabled', newstatus)
                    configuration.save()
                    status = newstatus
        else:
            print('Touchpad-Indicator is not working')
        if status:
            print('Touchpad is enabled')
        else:
            print('Touchpad is disabled')
    exit(0)
