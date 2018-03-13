#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# touchpad-indicator.py
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
#
#
#

import gi
try:
    gi.require_version('Gtk', '3.0')
    gi.require_version('GLib', '2.0')
    gi.require_version('GdkPixbuf', '2.0')
    gi.require_version('AppIndicator3', '0.1')
    gi.require_version('Notify', '0.7')
except Exception as e:
    print(e)
    exit(-1)
from gi.repository import Gtk
from gi.repository import GdkPixbuf
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Notify
from gi.repository import GLib
import os
import sys
import webbrowser
import subprocess
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from optparse import OptionParser
from watchdog import is_mouse_plugged
from touchpad import Touchpad
from touchpad import SYNAPTICS, LIBINPUT, EVDEV
from configurator import Configuration
from preferences_dialog import PreferencesDialog
from comun import _
from keyboard_monitor import KeyboardMonitor
import time
import comun
import machine_information
import shlex
import device_list


def ejecuta(comando):
    args = shlex.split(comando)
    subprocess.Popen(args, bufsize=10000, stdout=subprocess.PIPE)
    return 1


def add2menu(menu, text=None, icon=None, conector_event=None,
             conector_action=None):
    if text is not None:
        menu_item = Gtk.ImageMenuItem.new_with_label(text)
        if icon:
            image = Gtk.Image.new_from_file(icon)
            menu_item.set_image(image)
            menu_item.set_always_show_image(True)
    else:
        if icon is None:
            menu_item = Gtk.SeparatorMenuItem()
        else:
            menu_item = Gtk.ImageMenuItem.new_from_file(icon)
            menu_item.set_always_show_image(True)
    if conector_event is not None and conector_action is not None:
        menu_item.connect(conector_event, conector_action)
    menu_item.show()
    menu.append(menu_item)
    return menu_item


class SlimbookTouchpad(dbus.service.Object):
    def __init__(self):
        bus_name = dbus.service.BusName('es.slimbook.SlimbookTouchpad',
                                        bus=dbus.SessionBus())
        dbus.service.Object.__init__(self,
                                     bus_name,
                                     '/es/slimbook/SlimbookTouchpad')
        self.about_dialog = None
        self.the_watchdog = None
        self.icon = comun.ICON
        self.active_icon = None
        self.attention_icon = None
        self.keyboardMonitor = None
        self.doItAfter = None
        self.enable_after = 0.2
        self.touchpad = Touchpad()

        self.last_time_keypressed = 0
        self.interval = 0
        self.time_watcher = 0

        self.notification = Notify.Notification.new('', '', None)
        self.indicator = appindicator.Indicator.new(
            'Slimbook-Touchpad',
            '',
            appindicator.IndicatorCategory.HARDWARE)

        menu = self.get_menu()
        self.indicator.set_menu(menu)
        self.indicator.connect('scroll-event', self.on_scroll)

        self.read_preferences(is_on_start=True)

    # ########### preferences related methods #################

    def theme_change(self, theme):
        """Change the icon theme of the indicator.
            If the theme selected is invalid set the "normal" theme.
            :param theme: the index of the selected theme."""
        self.active_icon = comun.STATUS_ICON[theme][0]
        self.attention_icon = comun.STATUS_ICON[theme][1]
        self.indicator.set_icon(self.active_icon)
        self.indicator.set_attention_icon(self.attention_icon)

    def on_mouse_plugged_change(self, status):
        """Prepare the indicator to respond to mouse_plugged events.
            :param status: if True the indicator will listen to the events."""

    # ################# main functions ####################
    def set_touch_enabled(self, enabled, isforwriting=False):
        """Enable or disable the touchpads and update the indicator status
            and menu items.
            :param enabled: If True enable the touchpads."""
        print('==== start set_touch_enabled =====')
        print('set_touch_enabled:', enabled)
        print('are_all_touchpad_enabled: ',
              self.touchpad.are_all_touchpad_enabled())
        if enabled and not self.touchpad.are_all_touchpad_enabled():
            print('==|==')
            if self.touchpad.enable_all_touchpads():
                print('==|== 1')
                if self.show_notifications and not isforwriting:
                    print('==|== 2')
                    self.show_notification('enabled')
                self.change_state_item.set_label(_('Disable Touchpad'))
                if self.indicator.get_status() !=\
                        appindicator.IndicatorStatus.PASSIVE:
                    GLib.idle_add(self.indicator.set_status,
                                  appindicator.IndicatorStatus.ACTIVE)
                if not isforwriting:
                    configuration = Configuration()
                    configuration.set('touchpad_enabled',
                                      self.touchpad.are_all_touchpad_enabled())
                    configuration.save()
        elif enabled and self.touchpad.are_all_touchpad_enabled():
            if self.show_notifications and not isforwriting:
                self.show_notification('enabled')
            self.change_state_item.set_label(_('Disable Touchpad'))
            if self.indicator.get_status() !=\
                    appindicator.IndicatorStatus.PASSIVE:
                GLib.idle_add(self.indicator.set_status,
                              appindicator.IndicatorStatus.ACTIVE)
            if not isforwriting:
                configuration = Configuration()
                configuration.set('touchpad_enabled',
                                  self.touchpad.are_all_touchpad_enabled())
                configuration.save()

        elif not enabled and self.touchpad.are_all_touchpad_enabled():
            print('==?==')
            if self.touchpad.disable_all_touchpads():
                print('==?== 1')
                if self.show_notifications and not isforwriting:
                    print('==?== 2')
                    self.show_notification('disabled')
                self.change_state_item.set_label(_('Enable Touchpad'))
                if self.indicator.get_status() !=\
                        appindicator.IndicatorStatus.PASSIVE:
                    GLib.idle_add(self.indicator.set_status,
                                  appindicator.IndicatorStatus.ATTENTION)
                if not isforwriting:
                    configuration = Configuration()
                    configuration.set('touchpad_enabled',
                                      self.touchpad.are_all_touchpad_enabled())
                    configuration.save()
        elif not enabled and not self.touchpad.are_all_touchpad_enabled():
            if self.show_notifications and not isforwriting:
                self.show_notification('disabled')
            self.change_state_item.set_label(_('Enable Touchpad'))
            if self.indicator.get_status() !=\
                    appindicator.IndicatorStatus.PASSIVE:
                GLib.idle_add(self.indicator.set_status,
                              appindicator.IndicatorStatus.ATTENTION)
            if not isforwriting:
                configuration = Configuration()
                configuration.set('touchpad_enabled',
                                  self.touchpad.are_all_touchpad_enabled())
                configuration.save()

    def show_notification(self, kind):
        """Show a notification of type kind"""
        if kind == 'enabled':
            self.notification.update(
                'Slimbook Touchpad',
                _('Touchpad Enabled'),
                self.active_icon)
        elif kind == 'disabled':
            self.notification.update(
                'Slimbook Touchpad',
                _('Touchpad Disabled'),
                self.attention_icon)
        try:
            self.notification.show()
        except Exception as e:
            print(e)

    @dbus.service.method(dbus_interface='es.slimbook.SlimbookTouchpad')
    def on_mouse_detected_plugged(self):
        if self.on_mouse_plugged and self.touchpad.are_all_touchpad_enabled():
            self.change_state_item.set_sensitive(False)
            self.set_touch_enabled(False)
            if self.disable_on_typing:
                self.keyboardMonitor.stop()

    @dbus.service.method(dbus_interface='es.slimbook.SlimbookTouchpad')
    def on_mouse_detected_unplugged(self):
        if self.on_mouse_plugged and\
                not is_mouse_plugged() and\
                not self.touchpad.are_all_touchpad_enabled():
            self.change_state_item.set_sensitive(True)
            self.set_touch_enabled(True)
            if self.disable_on_typing:
                self.keyboardMonitor.start()

    @dbus.service.method(dbus_interface='es.slimbook.SlimbookTouchpad')
    def unhide(self):
        """Make the indicator icon visible again, if needed."""
        if self.indicator.get_status() == appindicator.IndicatorStatus.PASSIVE:
            if self.touchpad.are_all_touchpad_enabled():
                self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
            else:
                self.indicator.set_status(
                    appindicator.IndicatorStatus.ATTENTION)

    @dbus.service.method(dbus_interface='es.slimbook.SlimbookTouchpad')
    def change_state(self):
        if not self.on_mouse_plugged or\
                not is_mouse_plugged():
            is_touch_enabled = not self.touchpad.are_all_touchpad_enabled()
            self.set_touch_enabled(is_touch_enabled)

    @dbus.service.method(dbus_interface='es.slimbook.SlimbookTouchpad')
    def check_status_from_resume(self):
        configuration = Configuration()
        self.touchpad_enabled = configuration.get('touchpad_enabled')
        if self.touchpad_enabled != self.touchpad.are_all_touchpad_enabled():
            self.set_touch_enabled(self.touchpad_enabled)
        if self.on_mouse_plugged and not self.touchpad_enabled:
            if not is_mouse_plugged():
                self.set_touch_enabled(True)

    @dbus.service.method(dbus_interface='es.slimbook.SlimbookTouchpad')
    def check_status(self):
        configuration = Configuration()
        self.touchpad_enabled = configuration.get('touchpad_enabled')
        if self.touchpad_enabled != self.touchpad.are_all_touchpad_enabled():
            self.set_touch_enabled(self.touchpad_enabled)

    def launch_watchdog(self):
        """Call the watchdog and check if there was any mouse plugged."""

        if self.the_watchdog is None:
            self.the_watchdog = subprocess.Popen(comun.WATCHDOG)
        if is_mouse_plugged():
            self.change_state_item.set_sensitive(False)
            self.set_touch_enabled(False)

    def on_key_pressed(self, widget):
        self.set_touch_enabled(False, True)

    def on_key_released(self, widget):
        self.set_touch_enabled(True, True)

    def read_preferences(self, is_on_start=False):
        configuration = Configuration()
        self.first_time = configuration.get('first-time')
        self.version = configuration.get('version')
        self.shortcut_enabled = configuration.get('shortcut_enabled')
        self.autostart = configuration.get('autostart')
        self.on_mouse_plugged = configuration.get('on_mouse_plugged')

        self.start_hidden = configuration.get('start_hidden')
        self.show_notifications = configuration.get('show_notifications')
        self.theme = configuration.get('theme')
        self.touchpad_enabled = configuration.get('touchpad_enabled')

        self.on_start = configuration.get('on_start')
        self.on_end = configuration.get('on_end')

        self.shortcut = configuration.get('shortcut')
        self.ICON = comun.ICON
        self.active_icon = comun.STATUS_ICON[configuration.get('theme')][0]
        self.attention_icon = comun.STATUS_ICON[configuration.get('theme')][1]
        self.indicator.set_icon(self.active_icon)
        self.indicator.set_attention_icon(self.attention_icon)

        if not self.start_hidden:
            self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)

        # XINPUT
        # Para configurar el touchpad es necesario que esté habilitado
        are_all_touchpad_enabled = self.touchpad.are_all_touchpad_enabled()
        # If keyboardMonitor is working must stop
        if self.keyboardMonitor is not None:
            self.keyboardMonitor.stop()
            self.keyboardMonitor = None
        # If Watchdog is working must stop
        if self.the_watchdog is not None:
            self.the_watchdog.kill()
            self.the_watchdog = None
            self.change_state_item.set_sensitive(True)
            self.change_state()
        self.touchpad.enable_all_touchpads()
        time.sleep(1)
        self.interval = configuration.get('interval')
        self.touchpad.set_natural_scrolling_for_all(
            configuration.get('natural_scrolling'))
        self.touchpad.set_speed(configuration.get('speed') / 100.0)
        tipo = self.touchpad._get_type(self.touchpad._get_ids()[0])
        if tipo == LIBINPUT:
            if self.touchpad.has_tapping():
                self.touchpad.set_tapping(configuration.get('tapping'))

            if self.touchpad.can_edge_scrolling() is True and\
                    self.touchpad.can_two_finger_scrolling() is True:
                if configuration.get('edge_scrolling') is True and\
                        configuration.get('two_finger_scrolling') is True:
                    self.touchpad.set_two_finger_scrolling(True)
                elif configuration.get('edge_scrolling') is True:
                    self.touchpad.set_edge_scrolling(True)
                elif configuration.get('two_finger_scrolling') is True:
                    self.touchpad.set_two_finger_scrolling(True)
                else:
                    self.touchpad.set_two_finger_scrolling(False)
            elif self.touchpad.can_edge_scrolling() is True:
                self.touchpad.set_edge_scrolling(
                    self.configuration.get('edge_scrolling'))
            elif self.touchpad.can_two_finger_scrolling() is True:
                self.touchpad.set_two_finger_scrolling(
                    self.configuration.get('two_finger_scrolling'))
        elif tipo == SYNAPTICS:
            self.touchpad.set_two_finger_scrolling(
                configuration.get('two_finger_scrolling'))
            self.touchpad.set_edge_scrolling(
                configuration.get('edge_scrolling'))
            self.touchpad.set_circular_scrolling(
                configuration.get('cicular_scrolling'))
        self.disable_on_typing = configuration.get('disable_on_typing')
        if self.disable_on_typing:
            self.keyboardMonitor = KeyboardMonitor(self.interval)
            self.keyboardMonitor.connect('key_pressed', self.on_key_pressed)
            self.keyboardMonitor.connect('key_released', self.on_key_released)
            if self.on_mouse_plugged and is_mouse_plugged():
                self.keyboardMonitor.stop()
            else:
                self.keyboardMonitor.start()
        if self.on_mouse_plugged:
            self.launch_watchdog()
        time.sleep(1)
        if self.on_mouse_plugged and is_mouse_plugged():
                print('===', 1, '===')
                self.set_touch_enabled(False, False)
                self.change_state_item.set_sensitive(False)
        else:
            print('===', 2, '===')
            if is_on_start is True:
                print('===', 21, '===')
                if self.on_start == -1:
                    print('===', 211, '===')
                    self.set_touch_enabled(False, False)
                elif self.on_start == 1:
                    print('===', 212, '===')
                    self.set_touch_enabled(True, False)
                else:
                    print('===', 213, '===')
                    self.set_touch_enabled(are_all_touchpad_enabled, False)
            else:
                print('===', 2, '===')
                self.set_touch_enabled(True, False)

    # ################## menu creation ######################

    def get_help_menu(self):
        help_menu = Gtk.Menu()
        #
        add2menu(help_menu,
                 text=_('Homepage...'),
                 conector_event='activate',
                 conector_action=lambda x: webbrowser.open('\
https://slimbook.es'))
        add2menu(help_menu,
                 text=_('Get help online...'),
                 conector_event='activate',
                 conector_action=lambda x: webbrowser.open('\
https://answers.launchpad.net/~slimbook'))
        add2menu(help_menu,
                 text=_('Translate this application...'),
                 conector_event='activate',
                 conector_action=lambda x: webbrowser.open('\
https://translations.launchpad.net/touchpad-indicator'))
        add2menu(help_menu,
                 text=_('Report a bug...'),
                 conector_event='activate',
                 conector_action=lambda x: webbrowser.open('\
https://translations.launchpad.net/~slimbook'))
        add2menu(help_menu)
        web = add2menu(help_menu,
                       text=_('Homepage'),
                       conector_event='activate',
                       conector_action=lambda x: webbrowser.open('\
https://slimbook.es/tutoriales/linux/46-tutoriales/aplicaciones/96-slimbook-touchpad-activa-o-desactiva-tu-panel-tactil-con-este-indicador'))
        twitter = add2menu(help_menu,
                           text=_('Follow us in Twitter'),
                           conector_event='activate',
                           conector_action=lambda x: webbrowser.open('\
https://twitter.com/slimbookes'))
        googleplus = add2menu(help_menu,
                              text=_('Follow us in Google+'),
                              conector_event='activate',
                              conector_action=lambda x: webbrowser.open('\
https://plus.google.com/+SlimbookEs101'))
        facebook = add2menu(help_menu,
                            text=_('Follow us in Facebook'),
                            conector_event='activate',
                            conector_action=lambda x: webbrowser.open('\
https://www.facebook.com/slimbook.es/'))
        add2menu(help_menu)
        #
        web.set_image(Gtk.Image.new_from_file(os.path.join(comun.ICONDIR,
                                                           'slimbook.svg')))
        web.set_always_show_image(True)
        twitter.set_image(Gtk.Image.new_from_file(os.path.join(
            comun.ICONDIR, 'twitter.svg')))
        twitter.set_always_show_image(True)
        googleplus.set_image(Gtk.Image.new_from_file(os.path.join(
            comun.ICONDIR, 'google.svg')))
        googleplus.set_always_show_image(True)
        facebook.set_image(Gtk.Image.new_from_file(os.path.join(
            comun.ICONDIR, 'facebook.svg')))
        facebook.set_always_show_image(True)

        add2menu(help_menu)
        add2menu(help_menu,
                 text=_('About'),
                 conector_event='activate',
                 conector_action=self.on_about_item)

        help_menu.show()
        return(help_menu)

    def get_menu(self):
        """Create and populate the menu."""
        menu = Gtk.Menu()

        self.change_state_item = add2menu(
            menu,
            text=_('Disable Touchpad'),
            conector_event='activate',
            conector_action=self.on_change_state_item)
        add2menu(
            menu,
            text=_('Hide icon'),
            conector_event='activate',
            conector_action=self.on_hide_item)
        add2menu(
            menu,
            text=_('Preferences'),
            conector_event='activate',
            conector_action=self.on_preferences_item)

        add2menu(menu)

        menu_help = add2menu(menu, text=_('Help'))
        menu_help.set_submenu(self.get_help_menu())
        add2menu(menu)
        add2menu(
            menu,
            text=_('Exit'),
            conector_event='activate',
            conector_action=self.on_quit_item)

        menu.show()
        return(menu)

    def get_about_dialog(self):
        """Create and populate the about dialog."""
        about_dialog = Gtk.AboutDialog()
        about_dialog.set_name(comun.APPNAME)
        about_dialog.set_version(comun.VERSION)
        about_dialog.set_copyright(
            'Copyrignt (c) 2010-2018\nMiguel Angel Santamaría Rogado\
\nLorenzo Carbonell Cerezo')
        about_dialog.set_comments(_('An indicator for the Touchpad'))
        about_dialog.set_license('''
This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your option)
any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along with
this program.  If not, see <http://www.gnu.org/licenses/>.''')
        about_dialog.set_website('http://www.slimbook.es')
        about_dialog.set_website_label('http://www.slimbook.es')
        about_dialog.set_authors([
            'Lorenzo Carbonell <https://launchpad.net/~lorenzo-carbonell>',
            'Miguel Angel Santamaría Rogado <https://launchpad.net/~gabiel>'])
        about_dialog.set_documenters([
            'Lorenzo Carbonell <https://launchpad.net/~lorenzo-carbonell>'])
        about_dialog.set_translator_credits('''
'Ander Elortondo <https://launchpad.net/~ander-elor>\n'+
'anyone28 <https://launchpad.net/~b4025475>\n'+
'Candido Fernandez <https://launchpad.net/~candidinho>\n'+
'Fitoschido <https://launchpad.net/~fitoschido>\n'+
'Giorgi Maghlakelidze <https://launchpad.net/~dracid>\n'+
'ipadro <https://launchpad.net/~ivan-patfran>\n'+
'Javier García Díaz <https://launchpad.net/~jgd>\n'+
'Jiri Grönroos <https://launchpad.net/~jiri-gronroos>\n'+
'José Roitberg <https://launchpad.net/~roitberg>\n'+
'Lorenzo Carbonell <https://launchpad.net/~lorenzo-carbonell>\n'+
'Mantas Kriaučiūnas <https://launchpad.net/~mantas>\n'+
'Marek Tyburec <https://launchpad.net/~marek-tyburec>\n'+
'Miguel Anxo Bouzada <https://launchpad.net/~mbouzada>\n'+
'Montes Morgan <https://launchpad.net/~montes-morgan>\n'+
'Nur Kholis Majid <https://launchpad.net/~kholis>\n'+
'pibe <https://launchpad.net/~pibe>\n'+
'rodion <https://launchpad.net/~rodion-samusik>\n'+
'Velikanov Dmitry <https://launchpad.net/~velikanov-dmitry>\n'+
'XsLiDian <https://launchpad.net/~xslidian>\n'+
'Yared Hufkens <https://launchpad.net/~w38m4570r>\n''')
        about_dialog.set_icon(GdkPixbuf.Pixbuf.new_from_file(comun.ICON))
        about_dialog.set_logo(GdkPixbuf.Pixbuf.new_from_file(os.path.join(
            comun.ICONDIR, 'logo1.jpg')))
        about_dialog.set_program_name(comun.APPNAME)
        return about_dialog

    # ##################### callbacks for the menu #######################

    def on_scroll(self, widget, steps, direcction):
        self.change_state()

    def on_change_state_item(self, widget, data=None):
        self.change_state()

    def on_hide_item(self, widget, data=None):
        self.indicator.set_status(appindicator.IndicatorStatus.PASSIVE)

    def on_preferences_item(self, widget, data=None):
        widget.set_sensitive(False)
        preferences_dialog = PreferencesDialog(False)
        if preferences_dialog.run() == Gtk.ResponseType.ACCEPT:
            preferences_dialog.close_ok()
            self.read_preferences()
        preferences_dialog.hide()
        preferences_dialog.destroy()
        # we need to change the status icons
        widget.set_sensitive(True)

    def on_quit_item(self, widget, data=None):
        print(1)
        if self.the_watchdog is not None:
            self.the_watchdog.kill()
        if self.keyboardMonitor is not None:
            self.keyboardMonitor.stop()
            self.keyboardMonitor = None

        if self.on_end == 1:
            self.touchpad.enable_all_touchpads()
        elif self.on_end == -1:
            self.touchpad.disable_all_touchpads()

        configuration = Configuration()
        configuration.set('is_working', False)
        configuration.save()
        exit(0)

    def on_about_item(self, widget, data=None):
        if self.about_dialog:
            self.about_dialog.present()
        else:
            self.about_dialog = self.get_about_dialog()
            self.about_dialog.run()
            self.about_dialog.destroy()
            self.about_dialog = None


def make_visible():
    """Get and call the unhide method of the running Touchpad-indicator."""

    bus = dbus.SessionBus()
    service = bus.get_object('es.slimbook.SlimbookTouchpad',
                             '/es/slimbook/SlimbookTouchpad')
    unhide = service.get_dbus_method('unhide',
                                     'es.slimbook.SlimbookTouchpad')
    unhide()


def change_status():
    """Get and call the change_state method of the running
        Touchpad-indicator."""

    bus = dbus.SessionBus()
    service = bus.get_object('es.slimbook.SlimbookTouchpad',
                             '/es/slimbook/SlimbookTouchpad')
    change_state = service.get_dbus_method('change_state',
                                           'es.slimbook.SlimbookTouchpad')
    change_state()


def main():
    DBusGMainLoop(set_as_default=True)
    bus = dbus.SessionBus()
    request = bus.request_name('es.slimbook.SlimbookTouchpad',
                               dbus.bus.NAME_FLAG_DO_NOT_QUEUE)
    if request == dbus.bus.REQUEST_NAME_REPLY_EXISTS or len(sys.argv) > 1:
        print('Another instance of SlimbookTouchpad is working')
        usage_msg = _('usage: %prog [options]')
        parser = OptionParser(usage=usage_msg, add_help_option=False)
        parser.add_option('-h', '--help',
                          action='store_true',
                          dest='help',
                          default=False,
                          help=_('show this help and exit.'))
        parser.add_option('-c', '--change-state',
                          action='store_true',
                          dest='change',
                          default=False,
                          help=_('change the touchpad state. If indicator is \
not running launch it.'))
        parser.add_option('-s', '--show-icon',
                          action='store_true',
                          dest='show',
                          default=False,
                          help=_('show the icon if indicator is hidden. \
Default action. If indicator is not running launch it.'))
        parser.add_option('-l', '--list-devices',
                          action='store_true',
                          dest='list',
                          default=False,
                          help=_('list devices'))
        (options, args) = parser.parse_args()
        if options.help:
            parser.print_help()
        elif options.list:
            device_list.list()
        elif options.change:
            change_status()
        else:  # show by default
            make_visible()
        exit(0)
    else:  # first!!!
        # ###################################################################
        print('#####################################################')
        print(machine_information.get_information())
        print('SlimbookTouchpad version: %s' % comun.VERSION)
        print('#####################################################')
        # ###################################################################
        Notify.init("touchpad-indicator")
        object = bus.get_object('es.slimbook.SlimbookTouchpad',
                                '/es/slimbook/SlimbookTouchpad')
        dbus.Interface(object, 'es.slimbook.SlimbookTouchpad')
        SlimbookTouchpad()
        Gtk.main()
    exit(0)


if __name__ == "__main__":
    main()
