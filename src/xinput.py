#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# touchpad.py
#
# Copyright (C) 2010,2011
# Lorenzo Carbonell Cerezo <lorenzo.carbonell.cerezo@gmail.com>
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


def run(comando):
    print(comando)
    args = shlex.split(comando)
    p = subprocess.Popen(args, bufsize=10000, stdout=subprocess.PIPE)
    answer = p.communicate()[0].decode('utf-8')
    return answer


def is_natural_scrolling():
    test_str = run('xinput list-props 13')
    regex = r'libinput\s*Natural\s*Scrolling\s*Enabled\s*\(\d*\):\s*(\d)'
    matches = re.search(regex, test_str)
    if matches is not None:
        print(matches[1])
        if str(matches[1]) == '1':
            return True
    return False


def set_natural_scrolling():
    test_str = run('xinput list-props 13')
    regex = r'libinput\s*Natural\s*Scrolling\s*Enabled\s*\((\d*)\)'
    matches = re.search(regex, test_str)
    if matches is not None:
        return run('xinput set-prop 13 %s 1' % matches[1])
    return False


if __name__ == '__main__':
    print(is_natural_scrolling())
    print(set_natural_scrolling())
