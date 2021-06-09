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

import os
import machine_information
import comun
import syslog
try:
    import pyudev
except Exception as e:
    print(e, 'Error: no pyudev installed.')

FILEOUTPUT = os.path.join(os.environ['HOME'], 'device_list.txt')


def print_device_attrib(Device, fileoutput=None):
    if Device:
        for key in Device.keys():
            print('{0} -> {1}'.format(key, Device[key]))
        sys_name = Device.sys_name
        if not sys_name:
            sys_name = ''
        sys_number = Device.sys_number
        if not sys_number:
            sys_number = ''
        print('------------------------------------------------------')
        print('sys_name: ' + sys_name)
        print('sys_number: ' + sys_number)
        for child in Device.children:
            child_sys_name = child.sys_name
            if not child_sys_name:
                child_sys_name = ''
            child_sys_number = child.sys_number
            if not child_sys_number:
                child_sys_number = ''
            print('%s: %s' % (child_sys_name, child_sys_number))
        if fileoutput is not None:
            fileoutput.write('---------------------------------------------\n')
            fileoutput.write('sys_name: ' + sys_name + '\n')
            fileoutput.write('sys_number: ' + sys_number + '\n')
            for child in Device.children:
                child_sys_name = child.sys_name
                if not child_sys_name:
                    child_sys_name = ''
                child_sys_number = child.sys_number
                if not child_sys_number:
                    child_sys_number = ''
                fileoutput.write('%s: %s\n' % (child_sys_name,
                                               child_sys_number))


def print_devices(kind, context, fileoutput=None):
    if kind == 'MOUSE':
        search = '---------------MICE----------------'
        devices_list = context.list_devices(subsystem='input',
                                            ID_INPUT_MOUSE=True)
    elif kind == 'TOUCHPAD':
        search = '-------------TOUCHPADS-------------'
        devices_list = context.list_devices(subsystem='input',
                                            ID_INPUT_TOUCHPAD=True)
    else:
        search = '-----------OTHER DEVICES-----------'
        devices_list = context.list_devices(subsystem='input')
    print('\n\n')
    print(search)
    for device in devices_list:
        print('device: ' + device.sys_name)
        print('device number: ' + str(device.sys_number))
        try:
            print('parent name: ' + device.parent['NAME'])
            print('parent attributes:')
            print_device_attrib(device.parent)
        except Exception as e:
            print(e, device.sys_name + ' has no parent')
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        print('device atributes:')
        print_device_attrib(device)
    if fileoutput is not None:
        fileoutput.write('\n\n')
        fileoutput.write(search + '\n')
        for device in devices_list:
            fileoutput.write('device: ' + device.sys_name + '\n')
            fileoutput.write('device number: ' + str(device.sys_number) + '\n')
            try:
                fileoutput.write('parent name: ' + device.parent['NAME'] +
                                 '\n')
                fileoutput.write('parent attributes:\n')
                print_device_attrib(device.parent, fileoutput)
            except Exception as e:
                fileoutput.write('Error: ' + str(e) + device.sys_name + ' has no parent\n')
            fileoutput.write('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n')
            fileoutput.write('device atributes:\n')
            print_device_attrib(device, fileoutput)


def header(fileoutput):
    fileoutput.write('#####################################################\n')
    fileoutput.write(machine_information.get_information())
    fileoutput.write('Touchpad-Indicator version: %s\n' % comun.VERSION)
    fileoutput.write('#####################################################\n')


def list():
    context = pyudev.Context()
    context.log_priority = syslog.LOG_EMERG
    fileoutput = open(FILEOUTPUT, 'w')
    header(fileoutput)
    print_devices('MOUSE', context, fileoutput)
    print_devices('TOUCHPAD', context, fileoutput)
    print_devices('OTHER', context, fileoutput)
    fileoutput.close()


if __name__ == "__main__":
    list()
    exit(0)
