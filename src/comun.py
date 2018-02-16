#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#
# com.py
#
# Copyright (C) 2010 - 2018
# Lorenzo Carbonell Cerezo <lorenzo.carbonell.cerezo@gmail.com>
# Copyright (C) 2010,2011,2012
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
#
#
#

import os
import sys
import locale
import gettext


def is_package():
    return __file__.find('src') < 0


APPNAME = 'Slimbook Touchpad'
APP = 'slimbook-touchpad'
APPCONF = APP + '.conf'


PARAMS = {
    'first-time': True,
    'version': '',
    'is_working': False,
    'shortcut_enabled': False,
    'autostart': False,
    'disable_touchpad_on_start_indicator': False,
    'on_mouse_plugged': False,
    'enable_on_exit': True,
    'disable_on_exit': False,
    'disable_on_typing': False,
    'seconds': 2,
    'start_hidden': False,
    'show_notifications': True,
    'theme': 'light',
    'touchpad_enabled': True,
    'natural_scrolling': False,
    'shortcut': '<Primary><Alt>c',
    'VertEdgeScroll': True,
    'HorizEdgeScroll': True,
    'CircularScrolling': True,
    'VertTwoFingerScroll': True,
    'HorizTwoFingerScroll': True,
    'TapButton1': 1,
    'TapButton2': 3,
    'TapButton3': 0
}

# check if running from source
STATUS_ICON = {}
if is_package():
    ROOTDIR = '/usr/share/'
    LANGDIR = os.path.join(ROOTDIR, 'locale-langpack')
    APPDIR = os.path.join(ROOTDIR, APP)
    ICONDIR = os.path.join(APPDIR, 'icons')
    SOCIALDIR = os.path.join(APPDIR, 'social')
    CHANGELOG = os.path.join(APPDIR, 'changelog')
else:
    ROOTDIR = os.path.dirname(__file__)
    LANGDIR = os.path.normpath(os.path.join(ROOTDIR, '../po'))
    APPDIR = ROOTDIR
    ICONDIR = os.path.normpath(os.path.join(APPDIR, '../data/icons'))
    DEBIANDIR = os.path.normpath(os.path.join(ROOTDIR, '../debian'))
    CHANGELOG = os.path.join(DEBIANDIR, 'changelog')

ICON = os.path.join(ICONDIR, 'slimbook-touchpad-normal-enabled.svg')
STATUS_ICON['normal'] = (os.path.join(ICONDIR,
                         'slimbook-touchpad-normal-enabled.svg'),
                         os.path.join(ICONDIR,
                         'slimbook-touchpad-normal-disabled.svg'))
STATUS_ICON['light'] = (os.path.join(ICONDIR,
                        'slimbook-touchpad-light-enabled.svg'),
                        os.path.join(ICONDIR,
                        'slimbook-touchpad-light-disabled.svg'))
STATUS_ICON['dark'] = (os.path.join(ICONDIR,
                       'slimbook-touchpad-dark-enabled.svg'),
                       os.path.join(ICONDIR,
                       'slimbook-touchpad-dark-disabled.svg'))


CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.config')
CONFIG_APP_DIR = os.path.join(CONFIG_DIR, APP)
CONFIG_FILE = os.path.join(CONFIG_APP_DIR, APPCONF)

AUTOSTART_DIR = os.path.join(CONFIG_DIR, 'autostart')
FILE_AUTO_START = os.path.join(AUTOSTART_DIR,
                               'slimbook-touchpad-autostart.desktop')
WATCHDOG = os.path.join(APPDIR, 'watchdog.py')

f = open(CHANGELOG, 'r')
line = f.readline()
f.close()
pos = line.find('(')
posf = line.find(')', pos)
VERSION = line[pos + 1: posf].strip()
if is_package():
    VERSION = VERSION + '-src'
####
try:
    current_locale, encoding = locale.getdefaultlocale()
    language = gettext.translation(APP, LANGDIR, [current_locale])
    language.install()
    print(language)
    if sys.version_info[0] == 3:
        _ = language.gettext
    else:
        _ = language.ugettext
except Exception as e:
    print(e)
    _ = str
