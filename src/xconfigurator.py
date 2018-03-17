#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of Touchpad-Indicator
#
# Copyright (C) 2010-2018 Lorenzo Carbonell<lorenzo.carbonell.cerezo@gmail.com>
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
import os
import subprocess
from subprocess import Popen, PIPE


XFCONFQUERY = '/usr/bin/xfconf-query'


def xfconfquery_exists():
    return os.path.exists(XFCONFQUERY)


def is_running(process):
    # From http://www.bloggerpolis.com/2011/05/\
    # how-to-check-if-a-process-is-running-using-python/
    # and http://richarddingwall.name/2009/06/18/\
    # windows-equivalents-of-ps-and-kill-commands/
    try:  # Linux/Unix
        s = subprocess.Popen(["ps", "axw"], stdout=subprocess.PIPE)
    except Exception as e:  # Windows
        print(e)
        s = subprocess.Popen(["tasklist", "/v"], stdout=subprocess.PIPE)
    for x in s.stdout:
        if re.search(process, x.decode()):
            return True
    return False


def get_desktop_environment():
    desktop_session = os.environ.get("DESKTOP_SESSION")
    # easier to match if we doesn't have  to deal with caracter cases
    if desktop_session is not None:
        desktop_session = desktop_session.lower()
        if desktop_session in ["gnome", "unity", "cinnamon", "mate",
                               "budgie-desktop", "xfce4", "lxde", "fluxbox",
                               "blackbox", "openbox", "icewm", "jwm",
                               "afterstep", "trinity", "kde"]:
            return desktop_session
        # ## Special cases ##
        # Canonical sets $DESKTOP_SESSION to Lubuntu rather than
        # LXDE if using LXDE.
        # There is no guarantee that they will not do the same with
        # the other desktop environments.
        elif "xfce" in desktop_session or\
                desktop_session.startswith("xubuntu"):
            return "xfce4"
        elif desktop_session.startswith("ubuntu"):
            return "unity"
        elif desktop_session.startswith("lubuntu"):
            return "lxde"
        elif desktop_session.startswith("kubuntu"):
            return "kde"
        elif desktop_session.startswith("razor"):  # e.g. razorkwin
            return "razor-qt"
        elif desktop_session.startswith("wmaker"):  # eg. wmaker-common
            return "windowmaker"
    if os.environ.get('KDE_FULL_SESSION') == 'true':
        return "kde"
    elif os.environ.get('GNOME_DESKTOP_SESSION_ID'):
        if "deprecated" not in os.environ.get(
                'GNOME_DESKTOP_SESSION_ID'):
            return "gnome2"
    # From http://ubuntuforums.org/showthread.php?t=652320
    elif is_running("xfce-mcs-manage"):
        return "xfce4"
    elif is_running("ksmserver"):
        return "kde"
    return "unknown"


def getoutput(cmd):
    val = Popen(cmd, shell=True, stdout=PIPE).communicate()[0].decode("utf-8")
    return val.rstrip().lstrip()


class XFCEConfiguration:
    def __init__(self, channel):
        self.channel = channel

    def get_keys(self):
        out = getoutput('xfconf-query -c %s -l' % self.channel)
        keys = []
        for key in out.split('\n'):
            if '\override' not in key:
                key = key.rstrip().lstrip()
                value = self.get_value(key)
                keys.append({'key': key, 'value': value})
        return keys

    def set_property(self, property, value):
        val = getoutput('xfconf-query -c %s --create --property "%s" \
--set "%s" --type string' % (self.channel, property, value))
        return val

    def reset_property(self, property):
        val = getoutput('xfconf-query -c %s --reset --property "%s"' % (
            self.channel, property))
        return val

    def get_value(self, property):
        if len(property) > 0:
            val = getoutput('xfconf-query -c %s --property "%s"' % (
                self.channel, property))
            return val
        return None

    def search_for_value_in_properties_startswith(self, startswith, value):
        found_keys = []
        keys = self.search_for_property_startswith(startswith)
        for key in keys:
            if key['value'] == value:
                found_keys.append(key)
        return found_keys

    def search_for_property_startswith(self, startswith):
        found_keys = []
        keys = self.get_keys()
        for key in keys:
            if key['key'].startswith(startswith) and key not in found_keys:
                found_keys.append(key)
        return found_keys


if __name__ == '__main__':
    print(get_desktop_environment())
    if get_desktop_environment() == 'xfce4' and xfconfquery_exists():
        key = '<Control><Alt>t'
        xfceconf = XFCEConfiguration('xfce4-keyboard-shortcuts')
        akeys = xfceconf.search_for_value_in_properties_startswith(
            '/commands/custom/',
            '/usr/share/slimbooktouchpad/change_touchpad_state.py')
        print('akeys: ' + str(akeys))
        if akeys:
            for akey in akeys:
                print('akey: ' + str(akey))
                xfceconf.reset_property(akey['key'])
        if True:
            key = key.replace('<Primary>', '<Control>')
            print(key)
            print(xfceconf.set_property(
                '/commands/custom/' + key,
                '/usr/share/slimbooktouchpad/change_touchpad_state.py'))
    exit(0)
