#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Report Ubuntu and Machine information
#
# Copyright (C) 2010 - 2018
# Lorenzo Carbonell Cerezo <lorenzo.carbonell.cerezo@gmail.com>
# Miguel Angel Santamaría Rogado <leibag@gmail.com>
# Copyright (C) 2010 - 2011
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

import shlex
import subprocess


def ejecuta(comando):
    args = shlex.split(comando)
    p = subprocess.Popen(args, bufsize=10000, stdout=subprocess.PIPE)
    valor = p.communicate()[0]
    return valor


def get_information():
    information = '#####################################################\n'
    information += ejecuta('lsb_release -a').decode('utf-8')
    information += 'Version:\t%s' % ejecuta('uname -m').decode('utf-8')
    information += '#####################################################\n'
    return information


if __name__ == '__main__':
    print(get_information())
    exit(0)
