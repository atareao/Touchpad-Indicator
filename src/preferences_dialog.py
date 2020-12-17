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

import gi
try:
    gi.require_version('Gtk', '3.0')
except Exception as e:
    print(e)
    exit(-1)
from gi.repository import Gtk
from gi.repository import Gdk
from dconfigurator import DConfManager
from xconfigurator import xfconfquery_exists
from xconfigurator import XFCEConfiguration
from xconfigurator import get_desktop_environment
import os
from configurator import Configuration
from touchpad import Touchpad
from touchpad import SYNAPTICS, LIBINPUT, EVDEV
import comun
from comun import _


def select_value_in_combo(combo, value):
    model = combo.get_model()
    for i, item in enumerate(model):
        if value == item[1]:
            combo.set_active(i)
            return
    combo.set_active(0)


def get_selected_value_in_combo(combo):
    model = combo.get_model()
    return model.get_value(combo.get_active_iter(), 1)


def set_autostart(autostart):
    if os.path.exists(comun.FILE_AUTO_START) and\
            not os.path.islink(comun.FILE_AUTO_START):
        os.remove(comun.FILE_AUTO_START)
    if autostart is True:
        if not os.path.exists(comun.AUTOSTART_DIR):
            os.makedirs(comun.AUTOSTART_DIR)
        if not os.path.islink(comun.FILE_AUTO_START):
            os.symlink(comun.FILE_AUTO_START_SRC, comun.FILE_AUTO_START)
    else:
        if os.path.islink(comun.FILE_AUTO_START):
            os.remove(comun.FILE_AUTO_START)


def get_shortcuts():
    values = []
    de = get_desktop_environment()
    if de == 'gnome':
        dcm = DConfManager('org.gnome.desktop.wm.keybindings')
        for key in dcm.get_keys():
            for each_element in dcm.get_value(key):
                if type(each_element) == str:
                    values.append(each_element)
                elif type(each_element) == list:
                    values.extend(each_element)
        dcm = DConfManager('org.gnome.settings-daemon.plugins.media-keys')
        for key in dcm.get_keys():
            each_element = dcm.get_value(key)
            if type(each_element) == str:
                values.append(each_element)
            elif type(each_element) == list:
                values.extend(each_element)
    elif de == 'cinnamon':
        dcm = DConfManager('org.cinnamon.desktop.keybindings.media-keys')
        for key in dcm.get_keys():
            for each_element in dcm.get_value(key):
                if type(each_element) == str:
                    values.append(each_element)
                elif type(each_element) == list:
                    values.extend(each_element)
        dcm = DConfManager('org.cinnamon.desktop.keybindings.wm')
        for key in dcm.get_keys():
            for each_element in dcm.get_value(key):
                if type(each_element) == str:
                    values.append(each_element)
                elif type(each_element) == list:
                    values.extend(each_element)
    elif de == 'mate':
        dcm = DConfManager('org.mate.SettingsDaemon.plugins.media-keys')
        for key in dcm.get_keys():
            values.append(dcm.get_value(key))
    return values


class PreferencesDialog(Gtk.Dialog):

    def __init__(self, is_synaptics):
        #
        Gtk.Dialog.__init__(self, 'Touchpad Indicator | ' + _('Preferences'),
                            None,
                            Gtk.DialogFlags.MODAL |
                            Gtk.DialogFlags.DESTROY_WITH_PARENT,
                            (Gtk.STOCK_CANCEL,
                             Gtk.ResponseType.REJECT,
                             Gtk.STOCK_OK,
                             Gtk.ResponseType.ACCEPT))
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        # self.set_size_request(400, 230)
        self.connect('close', self.close_application)
        self.set_icon_from_file(comun.ICON)
        self.is_synaptics = is_synaptics

        vbox0 = Gtk.VBox(spacing=5)
        vbox0.set_border_width(5)
        self.get_content_area().add(vbox0)

        notebook = Gtk.Notebook.new()
        vbox0.add(notebook)

        if get_desktop_environment() in ['unity', 'gnome', 'cinnamon', 'mate']:
            vbox1 = Gtk.VBox(spacing=5)
            vbox1.set_border_width(5)
            notebook.append_page(vbox1, Gtk.Label.new(_('Shortcut')))
            frame1 = Gtk.Frame()
            vbox1.pack_start(frame1, False, True, 1)
            grid1 = Gtk.Grid()
            grid1.set_row_spacing(10)
            grid1.set_column_spacing(10)
            grid1.set_margin_bottom(10)
            grid1.set_margin_left(10)
            grid1.set_margin_right(10)
            grid1.set_margin_top(10)
            frame1.add(grid1)

            label1 = Gtk.Label(_('Shortcut enabled'))
            label1.set_alignment(0, 0.5)
            grid1.attach(label1, 0, 0, 1, 1)
            self.checkbutton0 = Gtk.Switch()
            self.checkbutton0.connect('button-press-event',
                                      self.on_checkbutton0_clicked)
            grid1.attach(self.checkbutton0, 1, 0, 1, 1)
            #
            self.ctrl = Gtk.ToggleButton('Control')
            self.ctrl.set_sensitive(False)
            grid1.attach(self.ctrl, 2, 0, 1, 1)

            self.alt = Gtk.ToggleButton('Alt')
            self.alt.set_sensitive(False)
            grid1.attach(self.alt, 3, 0, 1, 1)

            self.entry11 = Gtk.Entry()
            self.entry11.set_editable(False)
            self.entry11.set_width_chars(4)
            self.entry11.connect('key-release-event',
                                 self.on_entry11_key_release_event)
            grid1.attach(self.entry11, 4, 0, 1, 1)

        vbox2 = Gtk.VBox(spacing=5)
        vbox2.set_border_width(5)
        notebook.append_page(vbox2, Gtk.Label.new(_('Actions')))
        frame2 = Gtk.Frame()
        vbox2.pack_start(frame2, True, True, 0)
        grid2 = Gtk.Grid()
        grid2.set_row_spacing(10)
        grid2.set_column_spacing(10)
        grid2.set_margin_bottom(10)
        grid2.set_margin_left(10)
        grid2.set_margin_right(10)
        grid2.set_margin_top(10)
        frame2.add(grid2)

        label = Gtk.Label(_('Disable touchpad when mouse plugged'))
        label.set_alignment(0, 0.5)
        grid2.attach(label, 0, 0, 1, 1)
        checkbutton2box = Gtk.HBox()
        self.checkbutton2 = Gtk.Switch()
        checkbutton2box.pack_start(self.checkbutton2, False, False, 2)
        these_are_not_mice_button = Gtk.Button.new_with_label(_('I declare that there are no mice plugged in'))
        these_are_not_mice_button.set_tooltip_text(_("If Touchpad Indicator is not " \
            "re-enabling the touchpad when you unplug your mouse, it might help to unplug all " \
            "mice and click on this"))
        these_are_not_mice_button.connect('clicked', self.on_invalid_mice_button)
        checkbutton2box.pack_end(these_are_not_mice_button, True, True, 0)
        grid2.attach(checkbutton2box, 1, 0, 1, 1)

        label = Gtk.Label(_('On Touchpad Indicator starts:'))
        label.set_alignment(0, 0.5)
        grid2.attach(label, 0, 1, 1, 1)

        self.on_start = {}
        self.on_start['none'] = Gtk.RadioButton()
        self.on_start['none'].set_label(_('None'))
        grid2.attach(self.on_start['none'], 0, 2, 1, 1)

        self.on_start['enable'] = Gtk.RadioButton(group=self.on_start['none'])
        self.on_start['enable'].set_label(_('Enable touchpad'))
        grid2.attach(self.on_start['enable'], 1, 2, 1, 1)

        self.on_start['disable'] = Gtk.RadioButton(group=self.on_start['none'])
        self.on_start['disable'].set_label(_('Disable touchpad'))
        grid2.attach(self.on_start['disable'], 2, 2, 1, 1)

        label = Gtk.Label(_('On Touchpad Indicator ends:'))
        label.set_alignment(0, 0.5)
        grid2.attach(label, 0, 3, 1, 1)

        self.on_end = {}
        self.on_end['none'] = Gtk.RadioButton()
        self.on_end['none'].set_label(_('None'))
        grid2.attach(self.on_end['none'], 0, 4, 1, 1)

        self.on_end['enable'] = Gtk.RadioButton(group=self.on_end['none'])
        self.on_end['enable'].set_label(_('Enable touchpad'))
        grid2.attach(self.on_end['enable'], 1, 4, 1, 1)

        self.on_end['disable'] = Gtk.RadioButton(group=self.on_end['none'])
        self.on_end['disable'].set_label(_('Disable touchpad'))
        grid2.attach(self.on_end['disable'], 2, 4, 1, 1)

        self.checkbutton8 = Gtk.CheckButton.new_with_label(
            _('Disable touchpad on typing'))
        self.checkbutton8.connect('toggled', self.on_checkbutton8_toggled)
        grid2.attach(self.checkbutton8, 0, 5, 1, 1)

        self.label_interval = Gtk.Label(_('Milliseconds to wait \
after the last key\npress before enabling the touchpad') + ':')
        grid2.attach(self.label_interval, 0, 6, 1, 1)
        #
        self.interval = Gtk.SpinButton()
        self.interval.set_adjustment(
            Gtk.Adjustment(500, 300, 10000, 100, 1000, 0))
        grid2.attach(self.interval, 1, 6, 1, 1)

        vbox3 = Gtk.VBox(spacing=5)
        vbox3.set_border_width(5)
        notebook.append_page(vbox3, Gtk.Label.new(_('General options')))
        frame3 = Gtk.Frame()
        vbox3.pack_start(frame3, True, True, 0)
        grid3 = Gtk.Grid()
        grid3.set_row_spacing(10)
        grid3.set_column_spacing(10)
        grid3.set_margin_bottom(10)
        grid3.set_margin_left(10)
        grid3.set_margin_right(10)
        grid3.set_margin_top(10)
        frame3.add(grid3)

        label = Gtk.Label(_('Autostart'))
        label.set_alignment(0, 0.5)
        grid3.attach(label, 0, 0, 1, 1)
        checkbutton1box = Gtk.HBox()
        self.checkbutton1 = Gtk.Switch()
        checkbutton1box.pack_start(self.checkbutton1, False, False, 0)
        grid3.attach(checkbutton1box, 1, 0, 1, 1)

        self.checkbutton5 = Gtk.CheckButton.new_with_label(_('Start hidden'))
        grid3.attach(self.checkbutton5, 0, 1, 1, 1)
        #
        self.checkbutton6 = Gtk.CheckButton.new_with_label(
            _('Show notifications'))
        grid3.attach(self.checkbutton6, 0, 2, 1, 1)

        vbox4 = Gtk.VBox(spacing=5)
        vbox4.set_border_width(5)
        notebook.append_page(vbox4,
                             Gtk.Label.new(_('Touchpad configuration')))
        frame4 = Gtk.Frame()
        vbox4.pack_start(frame4, True, True, 0)
        grid4 = Gtk.Grid()
        grid4.set_row_spacing(10)
        grid4.set_column_spacing(10)
        grid4.set_margin_bottom(10)
        grid4.set_margin_left(10)
        grid4.set_margin_right(10)
        grid4.set_margin_top(10)
        frame4.add(grid4)

        label = Gtk.Label(_('Natural scrolling'))
        label.set_alignment(0, 0.5)
        grid4.attach(label, 0, 0, 1, 1)
        checkbutton46box = Gtk.HBox()
        self.checkbutton46 = Gtk.Switch()
        checkbutton46box.pack_start(self.checkbutton46, False, False, 0)
        grid4.attach(checkbutton46box, 1, 0, 1, 1)

        self.speed = None

        tp = Touchpad()
        if tp.is_there_touchpad():
            tipo = tp.get_driver()
            if tipo == SYNAPTICS:
                label = Gtk.Label(_('Touchpad speed'))
                label.set_alignment(0, 0.5)
                grid4.attach(label, 0, 1, 1, 1)
                self.speed = Gtk.Scale()
                self.speed.set_digits(0)
                self.speed.set_adjustment(
                    Gtk.Adjustment(0, -100, 100, 1, 10, 0))
                grid4.attach(self.speed, 1, 1, 2, 1)
                label = Gtk.Label(_('Two finger scrolling'))
                label.set_alignment(0, 0.5)
                grid4.attach(label, 0, 2, 1, 1)
                two_finger_scrollingbox = Gtk.HBox()
                self.two_finger_scrolling = Gtk.Switch()
                two_finger_scrollingbox.pack_start(
                    self.two_finger_scrolling, False, False, 0)
                grid4.attach(two_finger_scrollingbox, 1, 2, 1, 1)
                label = Gtk.Label(_('Edge scrolling'))
                label.set_alignment(0, 0.5)
                grid4.attach(label, 0, 3, 1, 1)
                edge_scrollingbox = Gtk.HBox()
                self.edge_scrolling = Gtk.Switch()
                edge_scrollingbox.pack_start(
                    self.edge_scrolling, False, False, 0)
                grid4.attach(edge_scrollingbox, 1, 3, 1, 1)
                label = Gtk.Label(_('Circular scrolling'))
                label.set_alignment(0, 0.5)
                grid4.attach(label, 0, 4, 1, 1)
                cicular_scrollingbox = Gtk.HBox()
                self.cicular_scrolling = Gtk.Switch()
                cicular_scrollingbox.pack_start(
                    self.cicular_scrolling, False, False, 0)
                grid4.attach(cicular_scrollingbox, 1, 4, 1, 1)

                grid4.attach(Gtk.Separator(), 0, 5, 5, 1)

                label = Gtk.Label(_('Simulation'))
                label.set_alignment(0, 0.5)
                grid4.attach(label, 0, 6, 1, 1)

                label = Gtk.Label(_('Right top corner'))
                label.set_alignment(0, 0.5)
                grid4.attach(label, 0, 7, 1, 1)

                right_top_corner_store = Gtk.ListStore(str, int)
                right_top_corner_store.append([_('Disable'), 0])
                right_top_corner_store.append([_('Left button'), 1])
                right_top_corner_store.append([_('Middle button'), 2])
                right_top_corner_store.append([_('Right button'), 3])

                self.right_top_corner = Gtk.ComboBox.new()
                self.right_top_corner.set_model(right_top_corner_store)
                cell1 = Gtk.CellRendererText()
                self.right_top_corner.pack_start(cell1, True)
                self.right_top_corner.add_attribute(cell1, 'text', 0)
                grid4.attach(self.right_top_corner, 1, 7, 1, 1)

                label = Gtk.Label(_('Right bottom corner'))
                label.set_alignment(0, 0.5)
                grid4.attach(label, 2, 7, 1, 1)

                right_bottom_corner_store = Gtk.ListStore(str, int)
                right_bottom_corner_store.append([_('Disable'), 0])
                right_bottom_corner_store.append([_('Left button'), 1])
                right_bottom_corner_store.append([_('Middle button'), 2])
                right_bottom_corner_store.append([_('Right button'), 3])

                self.right_bottom_corner = Gtk.ComboBox.new()
                self.right_bottom_corner.set_model(right_bottom_corner_store)
                cell1 = Gtk.CellRendererText()
                self.right_bottom_corner.pack_start(cell1, True)
                self.right_bottom_corner.add_attribute(cell1, 'text', 0)
                grid4.attach(self.right_bottom_corner, 3, 7, 1, 1)

                label = Gtk.Label(_('Left top corner'))
                label.set_alignment(0, 0.5)
                grid4.attach(label, 0, 8, 1, 1)

                left_top_corner_store = Gtk.ListStore(str, int)
                left_top_corner_store.append([_('Disable'), 0])
                left_top_corner_store.append([_('Left button'), 1])
                left_top_corner_store.append([_('Middle button'), 2])
                left_top_corner_store.append([_('Right button'), 3])

                self.left_top_corner = Gtk.ComboBox.new()
                self.left_top_corner.set_model(left_top_corner_store)
                cell1 = Gtk.CellRendererText()
                self.left_top_corner.pack_start(cell1, True)
                self.left_top_corner.add_attribute(cell1, 'text', 0)
                grid4.attach(self.left_top_corner, 1, 8, 1, 1)

                label = Gtk.Label(_('Left bottom corner'))
                label.set_alignment(0, 0.5)
                grid4.attach(label, 2, 8, 1, 1)

                left_bottom_corner_store = Gtk.ListStore(str, int)
                left_bottom_corner_store.append([_('Disable'), 0])
                left_bottom_corner_store.append([_('Left button'), 1])
                left_bottom_corner_store.append([_('Middle button'), 2])
                left_bottom_corner_store.append([_('Right button'), 3])

                self.left_bottom_corner = Gtk.ComboBox.new()
                self.left_bottom_corner.set_model(left_bottom_corner_store)
                cell1 = Gtk.CellRendererText()
                self.left_bottom_corner.pack_start(cell1, True)
                self.left_bottom_corner.add_attribute(cell1, 'text', 0)
                grid4.attach(self.left_bottom_corner, 3, 8, 1, 1)

                label = Gtk.Label(_('One finger tap'))
                label.set_alignment(0, 0.5)
                grid4.attach(label, 0, 9, 1, 1)

                one_finger_tap_store = Gtk.ListStore(str, int)
                one_finger_tap_store.append([_('Disable'), 0])
                one_finger_tap_store.append([_('Left button'), 1])
                one_finger_tap_store.append([_('Middle button'), 2])
                one_finger_tap_store.append([_('Right button'), 3])

                self.one_finger_tap = Gtk.ComboBox.new()
                self.one_finger_tap.set_model(one_finger_tap_store)
                cell1 = Gtk.CellRendererText()
                self.one_finger_tap.pack_start(cell1, True)
                self.one_finger_tap.add_attribute(cell1, 'text', 0)
                grid4.attach(self.one_finger_tap, 1, 9, 1, 1)

                if tp.get_capabilities()['two-finger-detection'] is True:
                    label = Gtk.Label(_('Two finger tap'))
                    label.set_alignment(0, 0.5)
                    grid4.attach(label, 0, 10, 1, 1)

                    two_finger_tap_store = Gtk.ListStore(str, int)
                    two_finger_tap_store.append([_('Disable'), 0])
                    two_finger_tap_store.append([_('Left button'), 1])
                    two_finger_tap_store.append([_('Middle button'), 2])
                    two_finger_tap_store.append([_('Right button'), 3])

                    self.two_finger_tap = Gtk.ComboBox.new()
                    self.two_finger_tap.set_model(two_finger_tap_store)
                    cell1 = Gtk.CellRendererText()
                    self.two_finger_tap.pack_start(cell1, True)
                    self.two_finger_tap.add_attribute(cell1, 'text', 0)
                    grid4.attach(self.two_finger_tap, 1, 10, 1, 1)

                if tp.get_capabilities()['three-finger-detection'] is True:
                    label = Gtk.Label(_('Three finger tap'))
                    label.set_alignment(0, 0.5)
                    grid4.attach(label, 2, 10, 1, 1)

                    three_finger_tap_store = Gtk.ListStore(str, int)
                    three_finger_tap_store.append([_('Disable'), 0])
                    three_finger_tap_store.append([_('Left button'), 1])
                    three_finger_tap_store.append([_('Middle button'), 2])
                    three_finger_tap_store.append([_('Right button'), 3])

                    self.three_finger_tap = Gtk.ComboBox.new()
                    self.three_finger_tap.set_model(three_finger_tap_store)
                    cell1 = Gtk.CellRendererText()
                    self.three_finger_tap.pack_start(cell1, True)
                    self.three_finger_tap.add_attribute(cell1, 'text', 0)
                    grid4.attach(self.three_finger_tap, 3, 10, 1, 1)

                grid4.attach(Gtk.Separator(), 0, 11, 5, 1)
                label = Gtk.Label(_('Driver: Synaptics'))
                label.set_alignment(0, 0.5)
                grid4.attach(label, 0, 12, 1, 1)
            elif tipo == LIBINPUT:
                if tp.has_tapping():
                    label = Gtk.Label(_('Tapping'))
                    label.set_alignment(0, 0.5)
                    grid4.attach(label, 0, 1, 1, 1)
                    tappingbox = Gtk.HBox()
                    self.tapping = Gtk.Switch()
                    tappingbox.pack_start(
                        self.tapping, False, False, 0)
                    grid4.attach(tappingbox, 1, 1, 1, 1)
                label = Gtk.Label(_('Touchpad speed'))
                label.set_alignment(0, 0.5)
                grid4.attach(label, 0, 2, 1, 1)
                self.speed = Gtk.Scale()
                self.speed.set_size_request(300, 0)
                self.speed.set_digits(0)
                self.speed.set_adjustment(
                    Gtk.Adjustment(0, -100, 100, 1, 10, 0))
                grid4.attach(self.speed, 1, 2, 1, 1)
                if tp.can_two_finger_scrolling():
                    label = Gtk.Label(_('Two finger scrolling'))
                    label.set_alignment(0, 0.5)
                    grid4.attach(label, 0, 3, 1, 1)
                    two_finger_scrollingbox = Gtk.HBox()
                    self.two_finger_scrolling = Gtk.Switch()
                    self.two_finger_scrolling.connect(
                        'state-set', self.on_two_finger_scrolling_changed)
                    two_finger_scrollingbox.pack_start(
                        self.two_finger_scrolling, False, False, 0)
                    grid4.attach(two_finger_scrollingbox, 1, 3, 1, 1)
                if tp.can_edge_scrolling():
                    label = Gtk.Label(_('Edge scrolling'))
                    label.set_alignment(0, 0.5)
                    grid4.attach(label, 0, 4, 1, 1)
                    edge_scrollingbox = Gtk.HBox()
                    self.edge_scrolling = Gtk.Switch()
                    self.edge_scrolling.connect(
                        'state-set', self.on_edge_scrolling_changed)
                    edge_scrollingbox.pack_start(
                        self.edge_scrolling, False, False, 0)
                    grid4.attach(edge_scrollingbox, 1, 4, 1, 1)
                label = Gtk.Label(_('Driver: Libinput'))
                label.set_alignment(0, 0.5)
                grid4.attach(label, 0, 5, 1, 1)
            elif tipo == EVDEV:
                label = Gtk.Label(_('Touchpad speed'))
                label.set_alignment(0, 0.5)
                grid4.attach(label, 0, 1, 1, 1)
                self.speed = Gtk.Scale()
                self.speed.set_size_request(300, 0)
                self.speed.set_digits(0)
                self.speed.set_adjustment(
                    Gtk.Adjustment(0, -100, 100, 1, 10, 0))
                grid4.attach(self.speed, 1, 1, 1, 1)
                label = Gtk.Label(_('Driver: Evdev'))
                label.set_alignment(0, 0.5)
                grid4.attach(label, 0, 2, 1, 1)
        vbox6 = Gtk.VBox(spacing=5)
        vbox6.set_border_width(5)
        notebook.append_page(vbox6, Gtk.Label.new(_('Theme')))
        frame6 = Gtk.Frame()
        vbox6.pack_start(frame6, True, True, 0)
        grid6 = Gtk.Grid()
        grid6.set_row_spacing(10)
        grid6.set_column_spacing(10)
        grid6.set_margin_bottom(10)
        grid6.set_margin_left(10)
        grid6.set_margin_right(10)
        grid6.set_margin_top(10)
        frame6.add(grid6)

        label4 = Gtk.Label(_('Select theme') + ':')
        label4.set_alignment(0, 0.5)
        grid6.attach(label4, 0, 0, 1, 1)
        self.radiobutton1 = Gtk.RadioButton()
        image1 = Gtk.Image()
        image1.set_from_file(os.path.join(comun.ICONDIR,
                             'touchpad-indicator-light-enabled.svg'))
        self.radiobutton1.add(image1)
        grid6.attach(self.radiobutton1, 1, 0, 1, 1)

        self.radiobutton2 = Gtk.RadioButton(group=self.radiobutton1)
        image2 = Gtk.Image()
        image2.set_from_file(os.path.join(comun.ICONDIR,
                             'touchpad-indicator-dark-enabled.svg'))
        self.radiobutton2.add(image2)
        grid6.attach(self.radiobutton2, 2, 0, 1, 1)

        self.radiobutton3 = Gtk.RadioButton(group=self.radiobutton1)
        image3 = Gtk.Image()
        image3.set_from_file(os.path.join(comun.ICONDIR,
                             'touchpad-indicator-normal-enabled.svg'))
        self.radiobutton3.add(image3)
        grid6.attach(self.radiobutton3, 3, 0, 1, 1)

        self.load_preferences()

        self.show_all()

    def on_two_finger_scrolling_changed(self, widget, state):
        if state is True:
            if self.edge_scrolling.get_active():
                self.edge_scrolling.handler_block_by_func(
                    self.on_edge_scrolling_changed)
                self.edge_scrolling.set_active(False)
                self.edge_scrolling.handler_unblock_by_func(
                    self.on_edge_scrolling_changed)

    def on_edge_scrolling_changed(self, widget, state):
        if state is True:
            if self.two_finger_scrolling.get_active():
                self.two_finger_scrolling.handler_block_by_func(
                    self.on_two_finger_scrolling_changed)
                self.two_finger_scrolling.set_active(False)
                self.two_finger_scrolling.handler_unblock_by_func(
                    self.on_two_finger_scrolling_changed)

    def on_checkbutton8_toggled(self, widget):
        self.label_interval.set_sensitive(self.checkbutton8.get_active())
        self.interval.set_sensitive(self.checkbutton8.get_active())

    def on_checkbutton0_clicked(self, widget, data):
        self.entry11.set_sensitive(not widget.get_active())

    def on_checkbutton3_activate(self, widget):
        if self.checkbutton3.get_active() and self.checkbutton4.get_active():
            self.checkbutton4.set_active(False)

    def on_checkbutton4_activate(self, widget):
        if self.checkbutton3.get_active() and self.checkbutton4.get_active():
            self.checkbutton3.set_active(False)

    def on_invalid_mice_button(self, widget):
        import watchdog
        watchdog.blacklist_every_current_mouse()

    def close_application(self, widget):
        self.destroy()

    def messagedialog(self, title, message):
        dialog = Gtk.MessageDialog(None,
                                   Gtk.DialogFlags.MODAL,
                                   Gtk.MessageType.INFO,
                                   buttons=Gtk.ButtonsType.OK)
        dialog.set_markup("<b>%s</b>" % title)
        dialog.format_secondary_markup(message)
        dialog.run()
        dialog.destroy()

    def close_ok(self):
        self.save_preferences()

    def on_entry11_key_release_event(self, widget, event):
        actual_key = widget.get_text()
        key = event.keyval
        # numeros / letras mayusculas / letras minusculas
        if ((key > 47) and (key < 58)) or ((key > 64) and (key < 91)) or\
                ((key > 96) and (key < 123)):
            if Gdk.keyval_is_upper(event.keyval):
                keyval = Gdk.keyval_name(Gdk.keyval_to_lower(event.keyval))
            else:
                keyval = Gdk.keyval_name(event.keyval)
            self.entry11.set_text(keyval)
            key1 = ''
            key2 = None
            if self.ctrl.get_active() is True:
                key1 += '<Primary>'
                key2 = '<Control>'
            if self.alt.get_active() is True:
                key1 += '<Alt>'
                if key2 is not None:
                    key2 += '<Alt>'
            key1 += self.entry11.get_text().lower()
            if key2 is not None:
                key2 += self.entry11.get_text().lower()
            desktop_environment = get_desktop_environment()
            if desktop_environment == 'gnome' or\
                    desktop_environment == 'cinnamon' or\
                    desktop_environment == 'mate':
                shortcuts = get_shortcuts()
                if key1 in shortcuts or key2 in shortcuts:
                    dialog = Gtk.MessageDialog(
                        parent=self,
                        flags=(Gtk.DialogFlags.MODAL |
                               Gtk.DialogFlags.DESTROY_WITH_PARENT),
                        type=Gtk.MessageType.ERROR,
                        buttons=Gtk.ButtonsType.OK_CANCEL,
                        message_format=_('This shortcut <Control> + <Alt> +') +
                        keyval + _(' is assigned'))
                    msg = _('This shortcut <Control> + <Alt> + ') + keyval +\
                        _(' is assigned')
                    dialog.set_property('title', 'Error')
                    dialog.set_property('text', msg)
                    dialog.run()
                    dialog.destroy()
                    self.entry11.set_text(actual_key)
                else:
                    self.entry11.set_text(keyval)
                    self.key = keyval

    def load_preferences(self):
        configuration = Configuration()
        first_time = configuration.get('first-time')
        version = configuration.get('version')
        if first_time or version != comun.VERSION:
            configuration.set_defaults()
            configuration.read()
        if os.path.exists(comun.FILE_AUTO_START) and\
                not os.path.islink(comun.FILE_AUTO_START):
            os.remove(comun.FILE_AUTO_START)
        self.checkbutton1.set_active(os.path.islink(comun.FILE_AUTO_START))
        print(comun.FILE_AUTO_START)
        print('====', os.path.exists(comun.FILE_AUTO_START))
        self.checkbutton2.set_active(configuration.get('on_mouse_plugged'))

        desktop_environment = get_desktop_environment()
        print(desktop_environment)

        if desktop_environment == 'gnome' or\
                desktop_environment == 'unity':
            dcm = DConfManager('org.gnome.settings-daemon.plugins.media-keys.\
custom-keybindings.touchpad-indicator')
            shortcut = dcm.get_value('binding')
            if shortcut is None or len(shortcut) == 0:
                self.checkbutton0.set_active(False)
                self.entry11.set_text('')
            else:
                self.checkbutton0.set_active(True)
                self.ctrl.set_active(shortcut.find('<Control>') > -1)
                self.alt.set_active(shortcut.find('<Alt>') > -1)
                self.entry11.set_text(shortcut[-1:])
        elif desktop_environment == 'cinnamon':
            dcm = DConfManager('org.cinnamon.desktop.keybindings.\
custom-keybindings.touchpad-indicator')
            shortcuts = dcm.get_value('binding')
            if shortcuts is None or len(shortcuts) == 0:
                self.checkbutton0.set_active(False)
                self.entry11.set_text('')
            else:
                shortcut = shortcuts[0]
                self.checkbutton0.set_active(True)
                self.ctrl.set_active(shortcut.find('<Control>') > -1)
                self.alt.set_active(shortcut.find('<Alt>') > -1)
                self.entry11.set_text(shortcut[-1:])
        elif desktop_environment == 'mate':
            dcm = DConfManager('org.mate.desktop.keybindings.\
touchpad-indicator')
            shortcut = dcm.get_value('binding')
            if shortcut is None or len(shortcut) == 0:
                self.checkbutton0.set_active(False)
                self.entry11.set_text('')
            else:
                self.checkbutton0.set_active(True)
                self.ctrl.set_active(shortcut.find('<Control>') > -1)
                self.alt.set_active(shortcut.find('<Alt>') > -1)
                self.entry11.set_text(shortcut[-1:])
        option = configuration.get('on_start')
        if option == 0:
            self.on_start['none'].set_active(True)
        if option == 1:
            self.on_start['enable'].set_active(True)
        elif option == -1:
            self.on_start['disable'].set_active(True)

        option = configuration.get('on_end')
        if option == 0:
            self.on_end['none'].set_active(True)
        elif option == 1:
            self.on_end['enable'].set_active(True)
        elif option == -1:
            self.on_end['disable'].set_active(True)

        self.checkbutton5.set_active(configuration.get('start_hidden'))
        self.checkbutton6.set_active(configuration.get('show_notifications'))

        self.checkbutton8.set_active(configuration.get('disable_on_typing'))
        self.interval.set_value(configuration.get('interval'))
        self.label_interval.set_sensitive(self.checkbutton8.get_active())
        self.interval.set_sensitive(self.checkbutton8.get_active())

        option = configuration.get('theme')
        if option == 'light':
            self.radiobutton1.set_active(True)
        elif option == 'dark':
            self.radiobutton2.set_active(True)
        elif option == 'normal':
            self.radiobutton3.set_active(True)

        self.checkbutton46.set_active(configuration.get('natural_scrolling'))
        tp = Touchpad()
        if tp.is_there_touchpad():
            tipo = tp.get_driver()
            if tipo == SYNAPTICS:
                self.two_finger_scrolling.set_active(
                    configuration.get('two_finger_scrolling'))
                self.edge_scrolling.set_active(
                    configuration.get('edge_scrolling'))
                self.cicular_scrolling.set_active(
                    configuration.get('cicular_scrolling'))
                select_value_in_combo(self.right_top_corner,
                                      configuration.get('right-top-corner'))
                select_value_in_combo(self.right_bottom_corner,
                                      configuration.get('right-bottom-corner'))
                select_value_in_combo(self.left_top_corner,
                                      configuration.get('left-top-corner'))
                select_value_in_combo(self.left_bottom_corner,
                                      configuration.get('left-bottom-corner'))
                select_value_in_combo(self.one_finger_tap,
                                      configuration.get('one-finger-tap'))
                if tp.get_capabilities()['two-finger-detection']:
                    select_value_in_combo(
                        self.two_finger_tap,
                        configuration.get('two-finger-tap'))
                if tp.get_capabilities()['three-finger-detection']:
                    select_value_in_combo(
                        self.three_finger_tap,
                        configuration.get('three-finger-tap'))
            elif tipo == LIBINPUT:
                if tp.can_two_finger_scrolling():
                    self.two_finger_scrolling.set_active(
                        configuration.get('two_finger_scrolling'))
                if tp.can_edge_scrolling():
                    self.edge_scrolling.set_active(
                        configuration.get('edge_scrolling'))
                if tp.has_tapping():
                    self.tapping.set_active(configuration.get('tapping'))
            if self.speed is not None:
                self.speed.set_value(configuration.get('speed'))

    def save_preferences(self):
        configuration = Configuration()
        configuration.set('first-time', False)
        configuration.set('version', comun.VERSION)
        if self.radiobutton1.get_active() is True:
            configuration.set('theme', 'light')
        elif self.radiobutton2.get_active() is True:
            configuration.set('theme', 'dark')
        else:
            configuration.set('theme', 'normal')

        if self.on_start['none'].get_active() is True:
            configuration.set('on_start', 0)
        elif self.on_start['enable'].get_active() is True:
            configuration.set('on_start', 1)
        else:
            configuration.set('on_start', -1)

        if self.on_end['none'].get_active() is True:
            configuration.set('on_end', 0)
        elif self.on_end['enable'].get_active() is True:
            configuration.set('on_end', 1)
        else:
            configuration.set('on_end', -1)

        configuration.set('autostart', self.checkbutton1.get_active())
        set_autostart(self.checkbutton1.get_active())
        configuration.set('on_mouse_plugged', self.checkbutton2.get_active())

        configuration.set('start_hidden', self.checkbutton5.get_active())
        configuration.set('show_notifications', self.checkbutton6.get_active())

        configuration.set('disable_on_typing', self.checkbutton8.get_active())
        configuration.set('interval', self.interval.get_value())

        configuration.set('natural_scrolling', self.checkbutton46.get_active())
        tp = Touchpad()
        if tp.is_there_touchpad():
            tipo = tp.get_driver()
            if tipo == SYNAPTICS:
                configuration.set(
                    'two_finger_scrolling',
                    self.two_finger_scrolling.get_active())
                configuration.set(
                    'edge_scrolling',
                    self.edge_scrolling.get_active())
                configuration.set(
                    'cicular_scrolling',
                    self.cicular_scrolling.get_active())
                configuration.set(
                    'right-top-corner',
                    get_selected_value_in_combo(self.right_top_corner))
                configuration.set(
                    'right-bottom-corner',
                    get_selected_value_in_combo(self.right_bottom_corner))
                configuration.set(
                    'left-top-corner',
                    get_selected_value_in_combo(self.left_top_corner))
                configuration.set(
                    'left-bottom-corner',
                    get_selected_value_in_combo(self.right_bottom_corner))
                configuration.set(
                    'one-finger-tap',
                    get_selected_value_in_combo(self.one_finger_tap))
                if tp.get_capabilities()['two-finger-detection']:
                    configuration.set(
                        'two-finger-tap',
                        get_selected_value_in_combo(self.two_finger_tap))
                if tp.get_capabilities()['three-finger-detection']:
                    configuration.set(
                        'three-finger-tap',
                        get_selected_value_in_combo(self.three_finger_tap))
            elif tipo == LIBINPUT:
                if tp.can_two_finger_scrolling():
                    configuration.set(
                        'two_finger_scrolling',
                        self.two_finger_scrolling.get_active())
                if tp.can_edge_scrolling():
                    configuration.set(
                        'edge_scrolling',
                        self.edge_scrolling.get_active())
                if tp.has_tapping():
                    configuration.set('tapping', self.tapping.get_active())
                configuration.set('speed', self.speed.get_value())
            elif tipo == EVDEV:
                configuration.set('speed', self.speed.get_value())

        import watchdog
        configuration.set('faulty-devices', list(watchdog.faulty_devices))

        configuration.save()
        desktop_environment = get_desktop_environment()

        if desktop_environment in ['gnome', 'unity', 'cinnamon', 'mate']:
            self.ctrl.set_active(True)
            self.alt.set_active(True)

        print(desktop_environment)
        if desktop_environment in ['gnome', 'unity']:
            dcm = DConfManager('org.gnome.settings-daemon.plugins.media-keys.\
custom-keybindings.touchpad-indicator')
            if self.checkbutton0.get_active() and\
                    len(self.entry11.get_text()) > 0:
                key1 = ''
                key2 = None
                if self.ctrl.get_active() is True:
                    key1 += '<Control>'
                    key2 = '<Primary>'
                if self.alt.get_active() is True:
                    key1 += '<Alt>'
                    if key2 is not None:
                        key2 += '<Alt>'
                key1 += self.entry11.get_text().lower()
                if key2 is not None:
                    key2 += self.entry11.get_text().lower()
                if key1 not in get_shortcuts() and key2 not in get_shortcuts():
                    dcm = DConfManager('org.gnome.settings-daemon.plugins.\
media-keys')
                    shortcuts = dcm.get_value('custom-keybindings')
                    key = '/org/gnome/settings-daemon/plugins/media-keys/\
custom-keybindings/touchpad-indicator/'
                    if key in shortcuts:
                        shortcuts.pop(shortcuts.index(key))
                        dcm.set_value('custom-keybindings', shortcuts)
                    if key not in shortcuts:
                        shortcuts.append(key)
                        dcm.set_value('custom-keybindings', shortcuts)
                    dcm = DConfManager('org.gnome.settings-daemon.plugins.media-keys.\
custom-keybindings.touchpad-indicator')
                    dcm.set_value('name', 'Touchpad-Indicator')
                    dcm.set_value('binding', key1)
                    dcm.set_value('command', '/usr/bin/python3 \
/usr/share/touchpad-indicator/change_touchpad_state.py')
            else:
                dcm.set_value('binding', '')
                dcm = DConfManager('org.gnome.settings-daemon.plugins.\
media-keys')
                shortcuts = dcm.get_value('custom-keybindings')
                key = '/org/gnome/settings-daemon/plugins/media-keys/\
custom-keybindings/touchpad-indicator/'
                if key in shortcuts:
                    shortcuts.pop(shortcuts.index(key))
                    dcm.set_value('custom-keybindings', shortcuts)
        elif desktop_environment == 'cinnamon':
            dcm = DConfManager('org.cinnamon.desktop.keybindings.\
custom-keybindings.touchpad-indicator')
            if self.checkbutton0.get_active() and\
                    len(self.entry11.get_text()) > 0:
                key1 = ''
                key2 = None
                if self.ctrl.get_active() is True:
                    key1 += '<Control>'
                    key2 = '<Primary>'
                if self.alt.get_active() is True:
                    key1 += '<Alt>'
                    if key2 is not None:
                        key2 += '<Alt>'
                key1 += self.entry11.get_text().lower()
                if key2 is not None:
                    key2 += self.entry11.get_text().lower()
                if key1 not in get_shortcuts() and key2 not in get_shortcuts():
                    dcm.set_value('name', 'Touchpad-Indicator')
                    dcm.set_value('binding', [key1])
                    dcm.set_value('command', '/usr/bin/python3 \
/usr/share/touchpad-indicator/change_touchpad_state.py')
                dcm = DConfManager('org.cinnamon.desktop.keybindings')
                shortcuts = dcm.get_value('custom-list')
                if 'touchpad-indicator' in shortcuts:
                    shortcuts.pop(shortcuts.index('touchpad-indicator'))
                    dcm.set_value('custom-list', shortcuts)
                if 'touchpad-indicator' not in shortcuts:
                    shortcuts.append('touchpad-indicator')
                    dcm.set_value('custom-list', shortcuts)
            else:
                dcm.set_value('binding', [])
                dcm = DConfManager('org.cinnamon.desktop.keybindings')
                shortcuts = dcm.get_value('custom-list')
                if 'touchpad-indicator' in shortcuts:
                    shortcuts.pop(shortcuts.index('touchpad-indicator'))
                    dcm.set_value('custom-list', shortcuts)
        elif desktop_environment == 'mate':
            dcm = DConfManager('org.mate.desktop.keybindings.\
touchpad-indicator')
            if self.checkbutton0.get_active() and\
                    len(self.entry11.get_text()) > 0:
                key1 = ''
                key2 = None
                if self.ctrl.get_active() is True:
                    key1 += '<Control>'
                    key2 = '<Primary>'
                if self.alt.get_active() is True:
                    key1 += '<Alt>'
                    if key2 is not None:
                        key2 += '<Alt>'
                key1 += self.entry11.get_text().lower()
                if key2 is not None:
                    key2 += self.entry11.get_text().lower()
                if key1 not in get_shortcuts() and key2 not in get_shortcuts():
                    dcm.set_value('name', 'Touchpad-Indicator')
                    dcm.set_value('binding', key1)
                    dcm.set_value('action', '/usr/bin/python3 \
/usr/share/touchpad-indicator/change_touchpad_state.py')
            else:
                dcm.set_value('binding', '')
        elif desktop_environment == 'xfce':
            if xfconfquery_exists():
                xfceconf = XFCEConfiguration('xfce4-keyboard-shortcuts')
                keys = xfceconf.search_for_value_in_properties_startswith(
                    '/commands/custom/',
                    '/usr/share/\
touchpad-indicator/change_touchpad_state.py')
                if keys:
                    for akey in keys:
                        xfceconf.reset_property(akey['key'])
                if self.checkbutton0.get_active():
                    key = key.replace('<Primary>', '<Control>')
                    xfceconf.set_property(
                        '/commands/custom/' + key,
                        '/usr/share/\
touchpad-indicator/change_touchpad_state.py')


if __name__ == "__main__":
    cm = PreferencesDialog(False)
    if cm.run() == Gtk.ResponseType.ACCEPT:
        cm.close_ok()
    cm.hide()
    cm.destroy()
    exit(0)
