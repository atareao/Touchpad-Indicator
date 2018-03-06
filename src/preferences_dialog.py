#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# preferences_dialog.py
#
# Copyright (C), 2010 - 2018
# Lorenzo Carbonell Cerezo <lorenzo.carbonell.cerezo@gmail.com>
# Copyright (C), 2010, 2011
# Miguel Angel Santamaría Rogado <leibag@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version, 3 of the License, or
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
import subprocess
from configurator import Configuration
from touchpad import Touchpad
from touchpad import SYNAPTICS, LIBINPUT, EVDEV
from utils import exists_psmouse
import webbrowser
import comun
from comun import _


def set_autostart(autostart):
    if autostart is True:
        if not os.path.islink(comun.FILE_AUTO_START):
            os.symlink(comun.FILE_AUTO_START_SRC, comun.FILE_AUTO_START)
    else:
        if os.path.islink(comun.FILE_AUTO_START):
            os.remove(comun.FILE_AUTO_START)


def get_shortcuts():
    values = []
    dcm = DConfManager('org.gnome.desktop.wm.keybindings')
    for key in dcm.get_keys():
        for each_element in dcm.get_value(key):
            values.append(each_element)
    dcm = DConfManager('org.gnome.settings-daemon.plugins.media-keys')
    for key in dcm.get_keys():
        each_element = dcm.get_value(key)
        if type(each_element) == str:
            values.append(each_element)
    return values


class PreferencesDialog(Gtk.Dialog):

    def __init__(self, is_synaptics):
        #
        Gtk.Dialog.__init__(self, 'Slimbook Touchpad | ' + _('Preferences'),
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
        self.ctrl = Gtk.ToggleButton('Ctrl')
        grid1.attach(self.ctrl, 2, 0, 1, 1)
        #
        self.alt = Gtk.ToggleButton('Alt')
        grid1.attach(self.alt, 3, 0, 1, 1)
        #
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
        self.checkbutton2 = Gtk.Switch()
        grid2.attach(self.checkbutton2, 1, 0, 1, 1)

        label = Gtk.Label(_('On Slimbook Touchpad starts:'))
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

        label = Gtk.Label(_('On Slimbook Touchpad ends:'))
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
        self.checkbutton1 = Gtk.Switch()
        grid3.attach(self.checkbutton1, 1, 0, 1, 1)

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

        label = Gtk.Label(_('Natural scrolling?'))
        label.set_alignment(0, 0.5)
        grid4.attach(label, 0, 0, 1, 1)
        self.checkbutton46 = Gtk.Switch()
        grid4.attach(self.checkbutton46, 1, 0, 1, 1)

        tp = Touchpad()
        if tp.is_there_touchpad():
            tipo = tp._get_type(tp._get_ids()[0])
            if tipo == SYNAPTICS:
                label = Gtk.Label(_('Touchpad speed?'))
                label.set_alignment(0, 0.5)
                grid4.attach(label, 0, 1, 1, 1)
                self.speed = Gtk.Scale()
                self.speed.set_size_request(300, 0)
                self.speed.set_digits(0)
                self.speed.set_adjustment(
                    Gtk.Adjustment(0, -100, 100, 1, 10, 0))
                grid4.attach(self.speed, 1, 1, 1, 1)
                label = Gtk.Label(_('Two finger scolling?'))
                label.set_alignment(0, 0.5)
                grid4.attach(label, 0, 2, 1, 1)
                self.two_finger_scrolling = Gtk.Switch()
                grid4.attach(self.two_finger_scrolling, 1, 2, 1, 1)
                label = Gtk.Label(_('Edge scolling?'))
                label.set_alignment(0, 0.5)
                grid4.attach(label, 0, 3, 1, 1)
                self.edge_scrolling = Gtk.Switch()
                grid4.attach(self.edge_scrolling, 1, 3, 1, 1)
                label = Gtk.Label(_('Circular scolling?'))
                label.set_alignment(0, 0.5)
                grid4.attach(label, 0, 4, 1, 1)
                self.cicular_scrolling = Gtk.Switch()
                grid4.attach(self.cicular_scrolling, 1, 4, 1, 1)
                label = Gtk.Label(_('Driver: Synaptics'))
                label.set_alignment(0, 0.5)
                grid4.attach(label, 0, 5, 1, 1)
            elif tipo == LIBINPUT:
                if tp.has_tapping():
                    label = Gtk.Label(_('Tapping?'))
                    label.set_alignment(0, 0.5)
                    grid4.attach(label, 0, 1, 1, 1)
                    self.tapping = Gtk.Switch()
                    grid4.attach(self.tapping, 1, 1, 1, 1)
                label = Gtk.Label(_('Touchpad speed?'))
                label.set_alignment(0, 0.5)
                grid4.attach(label, 0, 2, 1, 1)
                self.speed = Gtk.Scale()
                self.speed.set_size_request(300, 0)
                self.speed.set_digits(0)
                self.speed.set_adjustment(
                    Gtk.Adjustment(0, -100, 100, 1, 10, 0))
                grid4.attach(self.speed, 1, 2, 1, 1)
                if tp.can_two_finger_scrolling():
                    label = Gtk.Label(_('Two finger scolling?'))
                    label.set_alignment(0, 0.5)
                    grid4.attach(label, 0, 3, 1, 1)
                    self.two_finger_scrolling = Gtk.Switch()
                    self.two_finger_scrolling.connect(
                        'state-set', self.on_two_finger_scrolling_changed)
                    grid4.attach(self.two_finger_scrolling, 1, 3, 1, 1)
                if tp.can_edge_scrolling():
                    label = Gtk.Label(_('Edge scolling?'))
                    label.set_alignment(0, 0.5)
                    grid4.attach(label, 0, 4, 1, 1)
                    self.edge_scrolling = Gtk.Switch()
                    self.edge_scrolling.connect(
                        'state-set', self.on_edge_scrolling_changed)
                    grid4.attach(self.edge_scrolling, 1, 4, 1, 1)
                label = Gtk.Label(_('Driver: Libinput'))
                label.set_alignment(0, 0.5)
                grid4.attach(label, 0, 5, 1, 1)
                install_evdev = Gtk.Button(_('Install Evdev?'))
                install_evdev.connect('clicked', self.on_install_evdev)
                grid4.attach(install_evdev, 0, 6, 1, 1)
            elif tipo == EVDEV:
                label = Gtk.Label(_('Touchpad speed?'))
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
                install_libinput = Gtk.Button(_('Install Libinput?'))
                install_libinput.connect('clicked', self.on_install_libinput)
                grid4.attach(install_libinput, 0, 3, 1, 1)
        if not exists_psmouse():
            vbox5 = Gtk.VBox(spacing=5)
            vbox5.set_border_width(5)
            notebook.append_page(vbox5, Gtk.Label.new(_('Bugs')))
            frame5 = Gtk.Frame()
            vbox5.pack_start(frame5, True, True, 0)
            grid5 = Gtk.Grid()
            grid5.set_row_spacing(10)
            grid5.set_column_spacing(10)
            grid5.set_margin_bottom(10)
            grid5.set_margin_left(10)
            grid5.set_margin_right(10)
            grid5.set_margin_top(10)
            frame5.add(grid5)

            text = '''
<b>Problema:</b>

Al <b>suspender</b> el ordenador (acción que sucede al bajar la tapa) y \
reanudarlo, el <b>puntero del ratón</b> se va \na la <b>esquina superior \
derecha</b> y no vuelva a responder.

Esto es porque <b>el kernel no carga correctamente</b> el protocolo del \
touchpad.

<b>Solución:</b>

Editar e grub para añadir psmouse.proto=exps durante la carga del kernel.

<b>Nota importante:</b>
Una vez editado el grub, necesitarás reiniciar el equipo para rcuperar el \
control del touchpad.
'''
            label = Gtk.Label()
            label.set_markup(text)
            grid5.attach(label, 0, 0, 4, 2)

            button_psmouse = Gtk.Button('Edit the Grub?')
            button_psmouse.connect('clicked', self.on_edit_grub)
            grid5.attach(button_psmouse, 1, 3, 1, 1)

            button_more_info = Gtk.Button(_('Do you need more info?'))
            button_more_info.connect('clicked', self.on_more_info)
            grid5.attach(button_more_info, 2, 3, 1, 1)

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
                             'slimbook-touchpad-light-enabled.svg'))
        self.radiobutton1.add(image1)
        grid6.attach(self.radiobutton1, 1, 0, 1, 1)

        self.radiobutton2 = Gtk.RadioButton(group=self.radiobutton1)
        image2 = Gtk.Image()
        image2.set_from_file(os.path.join(comun.ICONDIR,
                             'slimbook-touchpad-dark-enabled.svg'))
        self.radiobutton2.add(image2)
        grid6.attach(self.radiobutton2, 2, 0, 1, 1)

        self.radiobutton3 = Gtk.RadioButton(group=self.radiobutton1)
        image3 = Gtk.Image()
        image3.set_from_file(os.path.join(comun.ICONDIR,
                             'slimbook-touchpad-normal-enabled.svg'))
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

    def on_more_info(self, widget):
        webbrowser.open('https://slimbook.es/it/tutoriales/linux/271-solucion-\
problema-touchpad-no-funciona-despues-de-suspender-o-cerrar-la-tapa-del-\
slimbook')

    def on_edit_grub(self, widget):
        subprocess.call(['slimbook-editgrub'])

    def on_install_evdev(self, widget):
        subprocess.call(['slimbook-installdriver', 'evdev'])

    def on_install_libinput(self, widget):
        subprocess.call(['slimbook-installdriver', 'libinput'])

    def on_checkbutton8_toggled(self, widget):
        self.label_interval.set_sensitive(self.checkbutton8.get_active())
        self.interval.set_sensitive(self.checkbutton8.get_active())

    def on_checkbutton0_clicked(self, widget, data):
        self.set_shortcut_sensitive(not widget.get_active())

    def set_shortcut_sensitive(self, sensitive):
        self.ctrl.set_sensitive(sensitive)
        self.alt.set_sensitive(sensitive)
        self.entry11.set_sensitive(sensitive)

    def on_checkbutton3_activate(self, widget):
        if self.checkbutton3.get_active() and self.checkbutton4.get_active():
            self.checkbutton4.set_active(False)

    def on_checkbutton4_activate(self, widget):
        if self.checkbutton3.get_active() and self.checkbutton4.get_active():
            self.checkbutton3.set_active(False)

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
            key = ''
            if self.ctrl.get_active() is True:
                key += '<Primary>'
            if self.alt.get_active() is True:
                key += '<Alt>'
            key += self.entry11.get_text()
            desktop_environment = get_desktop_environment()
            if desktop_environment == 'gnome':
                if key in get_shortcuts() and key != self.key:
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
        self.checkbutton1.set_active(os.path.islink(comun.FILE_AUTO_START))
        print(comun.FILE_AUTO_START)
        print('====', os.path.exists(comun.FILE_AUTO_START))
        self.checkbutton2.set_active(configuration.get('on_mouse_plugged'))

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

        self.checkbutton0.set_active(configuration.get('shortcut_enabled'))
        self.key = configuration.get('shortcut')
        self.shortcut_enabled = configuration.get('shortcut_enabled')
        if self.key.find('<Primary>') > -1:
            self.ctrl.set_active(True)
        if self.key.find('<Alt>') > -1:
            self.alt.set_active(True)
        self.entry11.set_text(self.key[-1:])
        self.set_shortcut_sensitive(self.checkbutton0.get_active())
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
            tipo = tp._get_type(tp._get_ids()[0])
            if tipo == SYNAPTICS:
                self.two_finger_scrolling.set_active(
                    configuration.get('two_finger_scrolling'))
                self.edge_scrolling.set_active(
                    configuration.get('edge_scrolling'))
                self.cicular_scrolling.set_active(
                    configuration.get('cicular_scrolling'))
            elif tipo == LIBINPUT:
                self.two_finger_scrolling.set_active(
                    configuration.get('two_finger_scrolling'))
                self.edge_scrolling.set_active(
                    configuration.get('edge_scrolling'))
                if tp.has_tapping():
                    self.tapping.set_active(configuration.get('tapping'))
            self.speed.set_value(configuration.get('speed'))

    def save_preferences(self):
        configuration = Configuration()
        configuration.set('first-time', False)
        configuration.set('version', comun.VERSION)
        key = ''
        if self.ctrl.get_active() is True:
            key += '<Primary>'
        if self.alt.get_active() is True:
            key += '<Alt>'
        key += self.entry11.get_text()
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

        configuration.set('shortcut_enabled', self.checkbutton0.get_active())
        configuration.set('autostart', self.checkbutton1.get_active())
        set_autostart(self.checkbutton1.get_active())
        configuration.set('on_mouse_plugged', self.checkbutton2.get_active())

        configuration.set('start_hidden', self.checkbutton5.get_active())
        configuration.set('show_notifications', self.checkbutton6.get_active())

        configuration.set('disable_on_typing', self.checkbutton8.get_active())
        configuration.set('interval', self.interval.get_value())
        configuration.set('shortcut', key)

        configuration.set('natural_scrolling', self.checkbutton46.get_active())
        tp = Touchpad()
        if tp.is_there_touchpad():
            tipo = tp._get_type(tp._get_ids()[0])
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

        configuration.save()

        desktop_environment = get_desktop_environment()
        if desktop_environment == 'gnome':
            print('gnom3')
            dcm = DConfManager('org.gnome.settings-daemon.plugins.media-keys')
            values = dcm.get_value('custom-keybindings')
            if self.checkbutton0.get_active():
                if '/org/gnome/settings-daemon/plugins/media-keys/\
custom-keybindings/slimbook-touchpad/' not in values:
                    values.append('/org/gnome/settings-daemon/plugins/\
media-keys/custom-keybindings/slimbook-touchpad/')
                    dcm.set_value('custom-keybindings', values)
                dcm = DConfManager('org.gnome.settings-daemon.plugins.\
media-keys.custom-keybindings.slimbook-touchpad')
                print(dcm.set_value('binding', key))
                print(dcm.set_value('command', '/usr/bin/python3 \
/usr/share/slimbook-touchpad/\
change_touchpad_state.py'))
                print(dcm.set_value('name', 'Touchpad-Indicator key binding'))
            else:
                if '/org/gnome/settings-daemon/plugins/media-keys/\
custom-keybindings/slimbook-touchpad/' in values:
                    values.remove('/org/gnome/settings-daemon/plugins/\
media-keys/custom-keybindings/slimbook-touchpad/')
                    dcm.set_value('custom-keybindings', values)
        elif desktop_environment == 'xfce':
            if xfconfquery_exists():
                xfceconf = XFCEConfiguration('xfce4-keyboard-shortcuts')
                keys = xfceconf.search_for_value_in_properties_startswith(
                    '/commands/custom/',
                    '/usr/share/\
slimbook-touchpad/change_touchpad_state.py')
                if keys:
                    for akey in keys:
                        xfceconf.reset_property(akey['key'])
                if self.checkbutton0.get_active():
                    key = key.replace('<Primary>', '<Control>')
                    xfceconf.set_property(
                        '/commands/custom/' + key,
                        '/usr/share/\
slimbook-touchpad/change_touchpad_state.py')


if __name__ == "__main__":
    cm = PreferencesDialog(False)
    if cm.run() == Gtk.ResponseType.ACCEPT:
            cm.close_ok()
    cm.hide()
    cm.destroy()
    exit(0)
