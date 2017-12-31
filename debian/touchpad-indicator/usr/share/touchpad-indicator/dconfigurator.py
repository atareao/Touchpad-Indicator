#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
#
# Copyright (C) 2012 - 2017 Lorenzo Carbonell
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

import gi
try:
    gi.require_version('Gio', '2.0')
    gi.require_version('GLib', '2.0')
except Exception as e:
    print(e)
    exit(-1)
from gi.repository import Gio
from gi.repository import GLib


class DConfManager(object):
    def __init__(self, key):
        self.setting = Gio.Settings(key)

    def get_keys(self):
        keys = []
        for entry in self.setting.list_keys():
            keys.append(entry)
        return keys

    def set_value(self, entry, value):
        if type(value) == str:
            self.setting.set_value(entry, GLib.Variant('s', value))
            return True
        elif type(value) == bool:
            self.setting.set_value(entry, GLib.Variant('b', value))
            return True
        elif type(value) == int:
            self.setting.set_value(entry, GLib.Variant('i', value))
            return True
        elif type(value) == list:
            self.setting.set_value(entry, GLib.Variant('as', value))
            return True
        return False

    def get_value(self, entry):
        value = self.setting.get_value(entry)
        if value.get_type_string().endswith('as'):
            return self.setting.get_strv(entry)
        elif value.get_type_string().endswith('s'):
            return self.setting.get_string(entry)
        elif value.get_type_string().endswith('b'):
            return self.setting.get_boolean(entry)
        elif value.get_type_string().endswith('i'):
            return self.setting.get_int(entry)
        return None

    def get_values(self):
        values = []
        for entry in self.setting.list_keys():
            values.append(self.get_value(entry))
        return values

    def get_children(self):
        print(self.setting.list_children())


if __name__ == '__main__':
    dcm = DConfManager('org.gnome.settings-daemon.plugins.media-keys')
    values = dcm.get_value('custom-keybindings')
    if '/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/\
touchpad-indicator/' in values:
        values.remove('/org/gnome/settings-daemon/plugins/media-keys/\
custom-keybindings/touchpad-indicator/')
        dcm.set_value('custom-keybindings', values)
    else:
        values.append('/org/gnome/settings-daemon/plugins/media-keys/\
custom-keybindings/touchpad-indicator/')
        dcm.set_value('custom-keybindings', values)
    dcm = DConfManager('org.gnome.settings-daemon.plugins.media-keys.\
custom-keybindings.touchpad-indicator')
    dcm.get_keys()
    print(dcm.set_value('binding', '<Primary><Alt>p'))
    print(dcm.set_value('command', '/usr/bin/python3 /home/atareao_r/Dropbox/\
tp/raring/touchpad-indicator/src/change_touchpad_state.py'))
    print(dcm.set_value('name', 'Touchpad-Indicator'))
