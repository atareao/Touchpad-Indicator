#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# watchdog.py
#
# Copyright (C) 2010,2011
# Miguel Angel Santamaría Rogado <leibag@gmail.com>
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
#
#
#
import pyudev
import dbus
from time import sleep

on_mouse_detected_plugged = None
on_mouse_detected_unplugged = None
check_status = None
check_status_from_resume = None

faulty_devices = ['11/2/a/0',  # TPPS/2 IBM TrackPoint
                  '11/2/5/7326',  # ImPS/2 ALPS GlidePoint
                  '11/2/1/0']

udev_context = pyudev.Context()


def is_mouse_plugged(blacklist=faulty_devices):
    """Return True if there is any mouse connected.
    Handle timing conditions where the device disappears while checking.
    :param blacklist: list of devices to discard."""
    retry_count = 3
    answer = None
    while answer is None:
        try:
            answer = _is_mouse_plugged(blacklist)
        except pyudev.device.DeviceNotFoundAtPathError as e:
            retry_count -= 1
            if retry_count == 0:
                print('DeviceNotFoundAtPathError: retry limit exceeded')
                raise e
            else:
                print('DeviceNotFoundAtPathError: retry')
                sleep(1)
    return answer


def _is_mouse_plugged(blacklist=faulty_devices):
    """Return True if there is any mouse connected
       :param blacklist: list of devices to discard."""
    possible_mice = udev_context.list_devices(subsystem="input",
                                              ID_INPUT_MOUSE=True)
    mice_list = []

    if blacklist is not None:
        for mouse in possible_mice:
            if mouse.parent is not None and 'PRODUCT' in mouse.parent.keys()\
                    and mouse.parent['PRODUCT'] not in blacklist:
                mice_list.append(mouse)
    else:
        mice_list = list(possible_mice)
    print(mice_list)
    if len(mice_list) == 0:
        return False
    else:
        return True


def is_mouse(device, blacklist=faulty_devices):
    """Return True if device is a mouse.
       :param device: pyudev.core.Device
       :param blacklist: list of devices to discard."""
    if blacklist is not None:
        try:
            if device.parent is not None and 'PRODUCT' in device.parent.keys()\
                    and device.parent['PRODUCT'] in blacklist:
                return False
            elif 'PRODUCT' in device.keys() and device['PRODUCT'] in blacklist:
                return False
        except KeyError:
            # if no PRODUCT attribute, ignore the blacklist
            pass
    try:
        if device.asbool("ID_INPUT_MOUSE"):
            return True
        else:
            return False
    except KeyError:
        return False


def init_dbus():
    """Initialize dbus parameters"""
    global on_mouse_detected_plugged
    global on_mouse_detected_unplugged
    global check_status
    global check_status_from_resume

    bus = dbus.SessionBus()
    try:
        touchpad_indicator_service = bus.get_object(
            'es.atareao.TouchpadIndicator',
            '/es/atareao/TouchpadIndicator')
        on_mouse_detected_plugged = touchpad_indicator_service.get_dbus_method(
            'on_mouse_detected_plugged',
            'es.atareao.TouchpadIndicator')
        on_mouse_detected_unplugged = \
            touchpad_indicator_service.get_dbus_method(
                'on_mouse_detected_unplugged',
                'es.atareao.TouchpadIndicator')
        check_status = touchpad_indicator_service.get_dbus_method(
            'check_status',
            'es.atareao.TouchpadIndicator')
        check_status_from_resume = touchpad_indicator_service.get_dbus_method(
            'check_status_from_resume',
            'es.atareao.TouchpadIndicator')
    except Exception as e:
        print(e, 'watchdog: Failed to initialize dbus.')
        exit(0)


def watch():
    """The watcher"""
    global on_mouse_detected_plugged
    global on_mouse_detected_unplugged
    global check_status
    global check_status_from_resume
    global udev_context

    monitor = pyudev.Monitor.from_netlink(udev_context)
    # TODO: filter also by device_type, so we can get rid of is_mouse()
    monitor.filter_by(subsystem="input", device_type=None)

    while True:
        try:
            for action, device in monitor:
                if is_mouse(device):
                    print('is mouse')
                    try:
                        if action == "add":
                            on_mouse_detected_plugged()
                            print('mouse added')
                        elif action == "remove":
                            on_mouse_detected_unplugged()
                            print('mouse removed')
                    except Exception as e:
                        print(e)
                        print('watchdog: failed to comunicate.')
                        exit(0)
        except IOError:
            print('watchdog: Return from suspend? Reseting the monitor.')
            # reset the monitor, altought not really needed
            # if we are coming back from suspend, because it only
            # fails the first iteration after the suspend
            if not _is_mouse_plugged():
                print('There is no mouse. Activating touchpad')
                on_mouse_detected_unplugged()
                sleep(1)
            monitor = pyudev.Monitor.from_netlink(udev_context)
            monitor.filter_by(subsystem="input", device_type=None)
            continue


if __name__ == "__main__":
    """Watcher for plug/unplug of mice from the system"""
    init_dbus()
    watch()
