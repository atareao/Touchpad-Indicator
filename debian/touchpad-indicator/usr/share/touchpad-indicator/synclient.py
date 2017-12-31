#! /usr/bin/python3
# -*- coding: utf-8 -*-
#
#
# Configure the Touchpad
#
# Copyright (C) 2013-2016 Lorenzo Carbonell
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
#
#
#
import shlex
import os.path
import subprocess


def run(comando):
    args = shlex.split(comando)
    p = subprocess.Popen(args, bufsize=10000, stdout=subprocess.PIPE)
    answer = p.communicate()[0].decode('utf-8')
    return answer


def run2(comando):
    args = shlex.split(comando)
    p = subprocess.Popen(args, bufsize=10000, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    answer = p.communicate()[1].decode('utf-8')
    return answer


class Synclient(object):
    def __init__(self):
        self.properties = {}
        self.properties['AccelFactor'] = None
        self.properties['AreaBottomEdge'] = None
        self.properties['AreaLeftEdge'] = None
        self.properties['AreaRightEdge'] = None
        self.properties['AreaTopEdge'] = None
        self.properties['BottomEdge'] = None
        self.properties['CircScrollDelta'] = None
        self.properties['CircScrollTrigger'] = None
        self.properties['CircularScrolling'] = None
        self.properties['ClickFinger1'] = None
        self.properties['ClickFinger2'] = None
        self.properties['ClickFinger3'] = None
        self.properties['ClickPad'] = None
        self.properties['ClickTime'] = None
        self.properties['CoastingFriction'] = None
        self.properties['CoastingSpeed'] = None
        self.properties['CornerCoasting'] = None
        self.properties['EmulateMidButtonTime'] = None
        self.properties['EmulateTwoFingerMinW'] = None
        self.properties['EmulateTwoFingerMinZ'] = None
        self.properties['FingerHigh'] = None
        self.properties['FingerLow'] = None
        self.properties['GrabEventDevice'] = None
        self.properties['HorizEdgeScroll'] = None
        self.properties['HorizHysteresis'] = None
        self.properties['HorizScrollDelta'] = None
        self.properties['HorizTwoFingerScroll'] = None
        self.properties['LBCornerButton'] = None
        self.properties['LeftEdge'] = None
        self.properties['LockedDrags'] = None
        self.properties['LockedDragTimeout'] = None
        self.properties['LTCornerButton'] = None
        self.properties['MaxDoubleTapTime'] = None
        self.properties['MaxSpeed'] = None
        self.properties['MaxTapMove'] = None
        self.properties['MaxTapTime'] = None
        self.properties['MinSpeed'] = None
        self.properties['PalmDetect'] = None
        self.properties['PalmMinWidth'] = None
        self.properties['PalmMinZ'] = None
        self.properties['PressureMotionMaxFactor'] = None
        self.properties['PressureMotionMaxZ'] = None
        self.properties['PressureMotionMinFactor'] = None
        self.properties['PressureMotionMinZ'] = None
        self.properties['RBCornerButton'] = None
        self.properties['RightEdge'] = None
        self.properties['RTCornerButton'] = None
        self.properties['SingleTapTimeout'] = None
        self.properties['TapAndDragGesture'] = None
        self.properties['TapButton1'] = None
        self.properties['TapButton2'] = None
        self.properties['TapButton3'] = None
        self.properties['TopEdge'] = None
        self.properties['TouchpadOff'] = None
        self.properties['VertEdgeScroll'] = None
        self.properties['VertHysteresis'] = None
        self.properties['VertScrollDelta'] = None
        self.properties['VertTwoFingerScroll'] = None
        self.read_configuration()

    @classmethod
    def createSynClient(cls):
        if run2('synclient').find('No synaptics driver loaded') > -1:
            return None
        return cls()

    def read_configuration(self):
        properties = {}
        for element in run('synclient -l').split('\n'):
            if element.find('=') > -1:
                proper, value = element.split('=')
                proper = proper.strip()
                value = value.strip()
                properties[proper] = value
        for key in self.properties.keys():
            if key in properties.keys():
                self.properties[key] = properties[key]

    def set(self, key, value):
        if key in self.properties.keys():
            run('synclient %s=%s' % (key, value))
        ans = self.get(key)
        return ans == value

    def get(self, key):
        self.read_configuration()
        if key in self.properties.keys():
            return self.properties[key]
        return None

    def __str__(self):
        items = []
        for key in self.properties.keys():
            items.append([key, self.properties[key]])
        items = sorted(items, key=lambda item: item[0])

        ans = '------------------------\n'
        for item in items:
            ans += "'%s':%s,\n" % (item[0], item[1])
        return ans

    def start(self):
        if self.is_running():
            if os.path.exists('/tmp/touchpad-indicator.pid'):
                return True
            else:
                self.stop()
        return run('syndaemon -d -p /tmp/touchpad-indicator.pid  &')

    def stop(self):
        if self.is_running():
            return run('killall syndaemon')
        True

    def is_running(self):
        return run('pidof syndaemon') != ''


if __name__ == '__main__':
    synclient = Synclient.createSynClient()
    '''synclient.stop()'''
    print(synclient.is_running())
    '''
    print(synclient)
    print(synclient.set('TouchpadOff','1'))
    time.sleep(3)
    print(synclient.set('TouchpadOff','0'))
    print(synclient)
    '''
    exit(0)
