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

bus = dbus.SessionBus()


if __name__ == '__main__':
    try:
        touchpad_indicator_service = bus.get_object(
            'es.atareao.TouchpadIndicator', '/es/atareao/TouchpadIndicator')
        change_state = touchpad_indicator_service.get_dbus_method(
            'change_state', 'es.atareao.TouchpadIndicator')
        change_state()
        print('Touchpad-Indicator is working')
    except dbus.exceptions.DBusException as argument:
        print(argument)
        print('Touchpad-Indicator is not working')
        touchpad = Touchpad()
        status = touchpad.are_all_touchpad_enabled()
        if status:
            touchpad.disable_all_touchpads()
        else:
            touchpad.enable_all_touchpads()
        newstatus = touchpad.are_all_touchpad_enabled()
        if newstatus != status:
            configuration = Configuration()
            configuration.set('touchpad_enabled', newstatus)
            configuration.save()
        if newstatus:
            print('Touchpad is enabled')
        else:
            print('Touchpad is disabled')
    exit(0)
