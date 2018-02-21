#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of slimbooktouchpad
#
# Copyright (C) 2016-2018 Lorenzo Carbonell
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
    gi.require_version('Gtk', '3.0')
    gi.require_version('GLib', '2.0')
    gi.require_version('Vte', '2.91')
except Exception as e:
    print(e)
    exit(1)
from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import Vte
import sys
import comun
from comun import _
from doitinbackground import DoItInBackground
from utils import is_package_installed

MARGIN = 5


class SmartTerminal(Vte.Terminal):
    def __init__(self, parent):
        Vte.Terminal.__init__(self)
        self.parent = parent

    def execute(self, commands):
        diib = DoItInBackground(self, commands)
        diib.connect('started', self.parent.start)
        diib.connect('done_one', self.parent.increase)
        diib.connect('ended', self.parent.end)
        diib.start()


class DriverInstallerDialog(Gtk.Window):
    def __init__(self, args):
        Gtk.Window.__init__(self)
        if len(args) != 2 or args[1].lower() not in ['libinput', 'evdev']:
            Gtk.main_quit()
        self.set_title(_('Install driver'))
        self.connect('delete-event', Gtk.main_quit)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_icon_from_file(comun.ICON)
        grid = Gtk.Grid()
        grid.set_margin_bottom(MARGIN)
        grid.set_margin_left(MARGIN)
        grid.set_margin_right(MARGIN)
        grid.set_margin_top(MARGIN)

        grid.set_column_spacing(MARGIN)
        grid.set_row_spacing(MARGIN)
        self.add(grid)

        self.driver = args[1].lower()
        if self.driver == 'libinput':
            label = Gtk.Label(_('Installing libinput driver...'))
        else:
            label = Gtk.Label(_('Installing evdev driver...'))
        label.set_alignment(0, 0.5)
        grid.attach(label, 0, 0, 2, 1)

        self.label = Gtk.Label('')
        self.label.set_alignment(0, 0.5)
        grid.attach(self.label, 0, 1, 2, 1)

        self.progressbar = Gtk.ProgressBar()
        grid.attach(self.progressbar, 0, 2, 4, 1)

        expander = Gtk.Expander()
        expander.connect('notify::expanded', self.on_expanded)
        grid.attach(expander, 0, 3, 4, 4)

        alignment = Gtk.Alignment()
        # alignment.set_padding(1, 0, 2, 2)
        alignment.props.xscale = 1
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)
        self.terminal = SmartTerminal(self)
        scrolledwindow.add(self.terminal)
        alignment.add(scrolledwindow)
        expander.add(alignment)

        self.button_ok = Gtk.Button(_('Ok'))
        self.button_ok.connect('clicked', self.on_button_ok_clicked)
        grid.attach(self.button_ok, 1, 8, 1, 1)

        self.button_cancel = Gtk.Button(_('Cancel'))
        self.button_cancel.connect('clicked', self.on_button_cancel_clicked)
        grid.attach(self.button_cancel, 2, 8, 1, 1)

        self.is_added = False
        self.show_all()
        self.progressbar.set_visible(False)
        self.label.set_visible(False)
        expander.set_expanded(True)

    def end(self, anobject, ok, *args):
        self.button_cancel.set_label(_('Exit'))
        self.button_cancel.set_sensitive(True)
        self.button_ok.set_sensitive(False)
        if ok is True:
            kind = Gtk.MessageType.INFO
            message = _('Driver installed')
        else:
            kind = Gtk.MessageType.ERROR
            message = _('Driver NOT installed')
        dialog = Gtk.MessageDialog(self, 0, kind,
                                   Gtk.ButtonsType.OK,
                                   message)
        dialog.run()
        dialog.destroy()

    def start(self, anobject, total, *args):
        self.button_ok.set_sensitive(False)
        self.button_cancel.set_sensitive(False)
        self.value = 0.0
        self.max_value = total

    def increase(self, anobject, command, *args):
        GLib.idle_add(self.label.set_text, _('Executing: %s') % command)
        self.value += 1.0
        fraction = self.value / self.max_value
        print(fraction)
        GLib.idle_add(self.progressbar.set_fraction, fraction)

    def decrease(self):
        self.value -= 1.0
        fraction = self.value / self.max_value
        GLib.idle_add(self.progressbar.set_fraction, fraction)

    def on_expanded(self, widget, data):
        if widget.get_property('expanded') is True:
            self.set_size_request(600, 300)
        else:
            self.set_size_request(600, 50)
            self.resize(600, 50)

    def on_button_cancel_clicked(self, button):
        self.destroy()

    def show_info(self):
        self.progressbar.set_visible(True)
        self.label.set_visible(True)

    def on_button_ok_clicked(self, button):
        GLib.idle_add(self.show_info)
        if self.driver == 'libinput':
            if is_package_installed('xserver-xorg-input-evdev'):
                commands = [
                    'apt update',
                    'apt install xserver-xorg-input-libinput -y',
                    'apt remove xserver-xorg-input-evdev -y']
            else:
                commands = [
                    'apt update',
                    'apt install xserver-xorg-input-libinput -y']
        elif self.driver == 'evdev':
            if is_package_installed('xserver-xorg-input-libinput'):
                commands = [
                    'apt update',
                    'apt install xserver-xorg-input-evdev -y',
                    'apt remove xserver-xorg-input-libinput -y']
            else:
                commands = [
                    'apt update',
                    'apt install xserver-xorg-input-evdev -y']
        else:
            commands = [
                'ls', 'ls', 'ls', 'ls', 'ls', 'ls', 'ls', 'ls']
        print(commands)
        self.terminal.execute(commands)


def main(args):
    print(args)
    if len(args) < 2:
        args.append('none')
    DriverInstallerDialog(args)
    Gtk.main()


if __name__ == '__main__':
    main(sys.argv)
    exit(0)
