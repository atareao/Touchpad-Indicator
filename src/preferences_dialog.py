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
import configparser
from configurator import Configuration
from touchpad import Touchpad
import comun
from comun import _


def set_autostart(autostart):
    if not os.path.exists(comun.AUTOSTART_DIR):
        os.makedirs(comun.AUTOSTART_DIR)
    if autostart:
        config = configparser.ConfigParser()
        config['Desktop Entry'] = {
            'Type': 'Application',
            'Icon': 'slimbook-touchpad',
            'Exec': '/usr/bin/slimbook-touchpad',
            'Hidden': 'false',
            'NoDisplay': 'false',
            'X-MATE-Autostart-Phase': 'Applications',
            'X-MATE-Autostart-Delay': '2',
            'X-MATE-Autostart-enabled': str(autostart),
            'X-GNOME-Autostart-Phase': 'Applications',
            'X-GNOME-Autostart-Delay': '2',
            'X-GNOME-Autostart-enabled': str(autostart)}
        with open(comun.FILE_AUTO_START, 'w') as autostart_file:
            config.write(autostart_file)
    else:
        if os.path.exists(comun.FILE_AUTO_START):
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

        self.checkbutton2 = Gtk.CheckButton.new_with_label(
            _('Disable touchpad when mouse plugged'))
        grid2.attach(self.checkbutton2, 0, 0, 1, 1)
        #
        self.checkbutton3 = Gtk.CheckButton.new_with_label(
            _('Enable touchpad on exit'))
        self.checkbutton3.connect('clicked',
                                  self.on_checkbutton3_activate)
        grid2.attach(self.checkbutton2, 0, 1, 1, 1)
        #
        self.checkbutton4 = Gtk.CheckButton.new_with_label(
            _('Disable touchpad on exit'))
        self.checkbutton4.connect('clicked', self.on_checkbutton4_activate)
        grid2.attach(self.checkbutton4, 0, 2, 1, 1)
        #
        self.checkbutton7 = Gtk.CheckButton.new_with_label(
            _('Disable touchpad when Touchpad-Indicator starts'))
        grid2.attach(self.checkbutton7, 0, 3, 1, 1)
        #
        self.checkbutton8 = Gtk.CheckButton.new_with_label(
            _('Disable touchpad on typing'))
        self.checkbutton8.connect('toggled', self.on_checkbutton8_toggled)
        grid2.attach(self.checkbutton8, 0, 4, 1, 1)
        #
        self.label_seconds = Gtk.Label('        ' + _('Milliseconds to wait \
after the last key press before enabling the touchpad') + ':')
        grid2.attach(self.label_seconds, 0, 5, 1, 1)
        #
        self.seconds = Gtk.SpinButton()
        self.seconds.set_adjustment(
            Gtk.Adjustment(1000, 100, 10000, 100, 1000, 0))
        grid2.attach(self.seconds, 1, 5, 1, 1)

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

        self.checkbutton46 = Gtk.CheckButton.new_with_label(
            _('Natural scrolling'))
        grid4.attach(self.checkbutton46, 0, 0, 1, 1)

        tp = Touchpad()
        if tp.is_there_touchpad():
            tipo = tp._get_type(tp._get_ids()[0])
            if tipo == 0:
                label = Gtk.Label(_('Driver: Synaptics'))
            elif tipo == 1:
                label = Gtk.Label(_('Driver: Libinput'))
            else:
                label = Gtk.Label(_('Driver: Evdev'))
            label.set_alignment(0, 0.5)
            grid4.attach(label, 0, 1, 1, 1)
            if tipo == 1:
                install_evdev = Gtk.Button(_('Install Evdev?'))
                install_evdev.connect('clicked', self.on_install_evdev)
                grid4.attach(install_evdev, 0, 2, 1, 1)
            elif tipo == 2:
                install_libinput = Gtk.Button(_('Install Libinput?'))
                install_libinput.connect('clicked', self.on_install_libinput)
                grid4.attach(install_libinput, 0, 2, 1, 1)

        if self.is_synaptics is True:

            mbuttons_store = Gtk.ListStore(str)
            mbuttons = ['None', 'Left mouse button', 'Middle mouse button',
                        'Right mouse button']
            for mbutton in mbuttons:
                mbuttons_store.append([mbutton])

            renderer_text = Gtk.CellRendererText()

            self.checkbutton41 = Gtk.CheckButton.new_with_label(
                _('Vertical scrolling'))
            grid4.attach(self.checkbutton41, 0, 0, 2, 1)
            self.checkbutton42 = Gtk.CheckButton.new_with_label(
                _('Horizontal scrolling'))
            grid4.attach(self.checkbutton42, 0, 1, 2, 1)
            self.checkbutton43 = Gtk.CheckButton.new_with_label(
                _('Circular scrolling'))
            grid4.attach(self.checkbutton43, 0, 2, 2, 1)
            self.checkbutton44 = Gtk.CheckButton.new_with_label(
                _('Two fingers vertical scrolling'))
            grid4.attach(self.checkbutton44, 0, 3, 2, 1)
            self.checkbutton45 = Gtk.CheckButton.new_with_label(
                _('Two fingers horizontal scrolling'))
            grid4.attach(self.checkbutton45, 0, 4, 2, 1)
            self.checkbutton46 = Gtk.CheckButton.new_with_label(
                _('Natural scrolling'))
            grid4.attach(self.checkbutton46, 0, 5, 2, 1)
            self.label_tapping1 = Gtk.Label(_('Tapping with one finger'))
            self.label_tapping1.set_alignment(0, 0.5)
            grid4.attach(self.label_tapping1, 0, 6, 1, 1)
            self.combobox47 = Gtk.ComboBox.new_with_model(mbuttons_store)
            self.combobox47.pack_start(renderer_text, True)
            self.combobox47.add_attribute(renderer_text, "text", 0)
            grid4.attach(self.combobox47, 1, 6, 1, 1)

            self.label_tapping2 = Gtk.Label(_('Tapping with two fingers'))
            self.label_tapping2.set_alignment(0, 0.5)
            grid4.attach(self.label_tapping2, 0, 7, 1, 1)
            self.combobox48 = Gtk.ComboBox.new_with_model(mbuttons_store)
            self.combobox48.pack_start(renderer_text, True)
            self.combobox48.add_attribute(renderer_text, "text", 0)
            grid4.attach(self.combobox48, 1, 7, 1, 1)

            self.label_tapping3 = Gtk.Label(_('Tapping with three fingers'))
            self.label_tapping3.set_alignment(0, 0.5)
            grid4.attach(self.label_tapping3, 0, 8, 1, 1)
            self.combobox49 = Gtk.ComboBox.new_with_model(mbuttons_store)
            self.combobox49.pack_start(renderer_text, True)
            self.combobox49.add_attribute(renderer_text, "text", 0)
            grid4.attach(self.combobox49, 1, 8, 1, 1)
        else:
            pass

        vbox5 = Gtk.VBox(spacing=5)
        vbox5.set_border_width(5)
        notebook.append_page(vbox5, Gtk.Label.new(_('Theme')))
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

        label4 = Gtk.Label(_('Select theme') + ':')
        label4.set_alignment(0, 0.5)
        grid5.attach(label4, 0, 0, 1, 1)
        self.radiobutton1 = Gtk.RadioButton()
        image1 = Gtk.Image()
        image1.set_from_file(os.path.join(comun.ICONDIR,
                             'slimbook-touchpad-light-enabled.svg'))
        self.radiobutton1.add(image1)
        grid5.attach(self.radiobutton1, 1, 0, 1, 1)

        self.radiobutton2 = Gtk.RadioButton(group=self.radiobutton1)
        image2 = Gtk.Image()
        image2.set_from_file(os.path.join(comun.ICONDIR,
                             'slimbook-touchpad-dark-enabled.svg'))
        self.radiobutton2.add(image2)
        grid5.attach(self.radiobutton2, 2, 0, 1, 1)

        self.radiobutton3 = Gtk.RadioButton(group=self.radiobutton1)
        image3 = Gtk.Image()
        image3.set_from_file(os.path.join(comun.ICONDIR,
                             'slimbook-touchpad-normal-enabled.svg'))
        self.radiobutton3.add(image3)
        grid5.attach(self.radiobutton3, 3, 0, 1, 1)

        self.load_preferences()

        self.show_all()

    def on_install_evdev(self, widget):
        subprocess.call(['installdriver', 'evdev'])

    def on_install_libinput(self, widget):
        subprocess.call(['installdriver', 'libinput'])

    def on_checkbutton8_toggled(self, widget):
        self.label_seconds.set_sensitive(self.checkbutton8.get_active())
        self.seconds.set_sensitive(self.checkbutton8.get_active())

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
        self.checkbutton0.set_active(configuration.get('shortcut_enabled'))
        self.checkbutton1.set_active(configuration.get('autostart'))
        self.checkbutton2.set_active(configuration.get('on_mouse_plugged'))
        self.checkbutton3.set_active(configuration.get('enable_on_exit'))
        self.checkbutton4.set_active(configuration.get('disable_on_exit'))
        self.checkbutton5.set_active(configuration.get('start_hidden'))
        self.checkbutton6.set_active(configuration.get('show_notifications'))
        self.checkbutton7.set_active(
            configuration.get('disable_touchpad_on_start_indicator'))
        self.checkbutton8.set_active(configuration.get('disable_on_typing'))
        self.seconds.set_value(configuration.get('seconds') * 1000)
        self.label_seconds.set_sensitive(self.checkbutton8.get_active())
        self.seconds.set_sensitive(self.checkbutton8.get_active())
        self.key = configuration.get('shortcut')
        self.shortcut_enabled = configuration.get('shortcut_enabled')
        if self.key.find('<Primary>') > -1:
            self.ctrl.set_active(True)
        if self.key.find('<Alt>') > -1:
            self.alt.set_active(True)
        self.entry11.set_text(self.key[-1:])
        option = configuration.get('theme')
        self.set_shortcut_sensitive(self.checkbutton0.get_active())
        if option == 'light':
            self.radiobutton1.set_active(True)
        if option == 'dark':
            self.radiobutton2.set_active(True)
        else:
            self.radiobutton3.set_active(True)

        self.checkbutton46.set_active(configuration.get('natural_scrolling'))

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
            theme = 'light'
        elif self.radiobutton2.get_active() is True:
            theme = 'dark'
        else:
            theme = 'normal'
        configuration.set('shortcut_enabled', self.checkbutton0.get_active())
        configuration.set('autostart', self.checkbutton1.get_active())
        set_autostart(self.checkbutton1.get_active())
        configuration.set('on_mouse_plugged', self.checkbutton2.get_active())
        configuration.set('enable_on_exit', self.checkbutton3.get_active())
        configuration.set('disable_on_exit', self.checkbutton4.get_active())
        configuration.set('start_hidden', self.checkbutton5.get_active())
        configuration.set('show_notifications', self.checkbutton6.get_active())
        configuration.set(
            'disable_touchpad_on_start_indicator',
            self.checkbutton7.get_active())
        configuration.set('disable_on_typing', self.checkbutton8.get_active())
        configuration.set('seconds', self.seconds.get_value() / 1000.0)
        configuration.set('shortcut', key)
        configuration.set('theme', theme)

        configuration.set('natural_scrolling', self.checkbutton46.get_active())
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
