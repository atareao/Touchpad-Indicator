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


def run(comando):
    args = shlex.split(comando)
    p = subprocess.Popen(args, bufsize=10000, stdout=subprocess.PIPE)
    valor = p.communicate()[0].decode('utf-8')
    return valor


class DistroInfo():
    def __init__(self):
        self.architecture = run('uname -m')
        test_str = run('lsb_release -a')
        regex = r'Distributor\s*ID:\s*(.*)\nDescription:\s*(.*)\nRelease:\s*(.*)\nCodename:\s*(.*)'
        matches = re.search(regex, test_str, re.M | re.I)
        if matches is not None:
            self.distributor = matches.group(1)
            self.description = matches.group(2)
            self.release = matches.group(3)
            self.codename = matches.group(4)
        else:
            self.distributor = ''
            self.description = ''
            self.release = ''
            self.codename = ''

    def __str__(self):
        information = 'Distributor: %s\n' % self.distributor
        information += 'Description: %s\n' % self.description
        information += 'Release: %s\n' % self.release
        information += 'Codename: %s\n' % self.codename
        information += 'Architecture: %s' % self.architecture
        return information


def get_information():
    information = '#####################################################\n'
    information += str(DistroInfo())
    information += '#####################################################\n'
    return information


if __name__ == '__main__':
    print(get_information())
    exit(0)
