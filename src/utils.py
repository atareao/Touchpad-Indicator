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

import subprocess
import shlex
from os.path import isfile, join, basename
import glob


def get_version():
    command = 'lsb_release -c'
    po = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, shell=False)
    out, err = po.communicate()
    return_code = po.wait()
    if return_code == 0:
        return out.decode().split('Codename:\t')[1].replace('\n', '')
    return None


def is_package_installed(package_name):
    command = 'dpkg-query --show --showformat="${db:Status-Status}\n" "%s"' % (
        package_name)
    po = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, shell=False)
    out, err = po.communicate()
    return_code = po.wait()
    if return_code == 0:
        return True
    return False


def is_ppa_repository_added(repository):
    if repository.find('/') and repository.startswith('ppa:'):
        repository = repository[4:]
        firstpart, secondpart = repository.split('/')
        mypath = '/etc/apt/sources.list.d'
        onlyfiles = [basename(f).replace('.list', '') for f in
                     glob.glob(join(mypath, '*.list'))
                     if isfile(join(mypath, f))]
        for element in onlyfiles:
            if element.startswith(firstpart) and \
                    element[len(firstpart):].find(secondpart) > -1:
                return True
    return False


if __name__ == '__main__':
    print(is_package_installed('my-weather-indicator'))
    print(is_package_installed('xserver-xorg-input-libinput'))
    print(get_version())
    print(is_ppa_repository_added('ppa:atareao/atareao'))
    print(exists_psmouse())