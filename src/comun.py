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

import os
import sys
import locale
import gettext

USRDIR = '/usr'


def is_package():
    return (__file__.startswith(USRDIR) or os.getcwd().startswith(USRDIR))


APPNAME = 'Touchpad Indicator'
APP = 'touchpad-indicator'
APPCONF = APP + '.conf'


PARAMS = {
    'first-time': True,
    'version': '',
    'is_working': False,
    'autostart': False,
    'on_mouse_plugged': False,
    'on_start': 1,
    'on_end': 1,
    'disable_on_typing': False,
    'interval': 600,
    'start_hidden': False,
    'show_notifications': True,
    'theme': 'normal',
    'touchpad_enabled': True,
    'natural_scrolling': True,
    'speed': 0.0,
    'tapping': True,
    'two_finger_scrolling': True,
    'edge_scrolling': False,
    'cicular_scrolling': True
}

# check if running from source
STATUS_ICON = {}
if is_package():
    ROOTDIR = '/usr/share/'
    LANGDIR = os.path.join(ROOTDIR, 'locale-langpack')
    APPDIR = os.path.join(ROOTDIR, APP)
    AUTOSTART_SOURCE_DIR = APPDIR
    ICONDIR = os.path.join(APPDIR, 'icons')
    SOCIALDIR = os.path.join(APPDIR, 'social')
    CHANGELOG = os.path.join(APPDIR, 'changelog')
else:
    ROOTDIR = os.path.dirname(__file__)
    LANGDIR = os.path.normpath(os.path.join(ROOTDIR, '../po'))
    APPDIR = ROOTDIR
    AUTOSTART_SOURCE_DIR = os.path.normpath(os.path.join(APPDIR, '../data'))
    ICONDIR = os.path.normpath(os.path.join(APPDIR, '../data/icons'))
    DEBIANDIR = os.path.normpath(os.path.join(ROOTDIR, '../debian'))
    CHANGELOG = os.path.join(DEBIANDIR, 'changelog')

ICON = os.path.join(ICONDIR, 'touchpad-indicator-normal-enabled.svg')
STATUS_ICON['normal'] = (os.path.join(ICONDIR,
                         'touchpad-indicator-normal-enabled.svg'),
                         os.path.join(ICONDIR,
                         'touchpad-indicator-normal-disabled.svg'))
STATUS_ICON['light'] = (os.path.join(ICONDIR,
                        'touchpad-indicator-light-enabled.svg'),
                        os.path.join(ICONDIR,
                        'touchpad-indicator-light-disabled.svg'))
STATUS_ICON['dark'] = (os.path.join(ICONDIR,
                       'touchpad-indicator-dark-enabled.svg'),
                       os.path.join(ICONDIR,
                       'touchpad-indicator-dark-disabled.svg'))


CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.config')
CONFIG_APP_DIR = os.path.join(CONFIG_DIR, APP)
CONFIG_FILE = os.path.join(CONFIG_APP_DIR, APPCONF)

AUTOSTART_DIR = os.path.join(CONFIG_DIR, 'autostart')
FILE_AUTO_START_NAME = 'touchpad-indicator-autostart.desktop'
FILE_AUTO_START_SRC = os.path.join(AUTOSTART_SOURCE_DIR, FILE_AUTO_START_NAME)
FILE_AUTO_START = os.path.join(AUTOSTART_DIR, FILE_AUTO_START_NAME)
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
