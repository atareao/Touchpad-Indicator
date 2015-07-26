#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
__author__="Lorenzo Carbonell"
__date__ ="$28-jul-2012$"
#
#
# Copyright (C) 2012 Lorenzo Carbonell
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
from gi.repository import Gio, GLib	

class DConfManager(object):
	def __init__(self,key):
		self.setting = Gio.Settings(key)

	def get_keys(self):
		keys = []
		for entry in self.setting.list_keys():
			keys.append(entry)
		return keys

	def set_value(self,entry,value):
		if type(value)==str:
			self.setting.set_value(entry,GLib.Variant('s',value))
			return True
		elif type(value)==bool:
			self.setting.set_value(entry,GLib.Variant('b',value))
			return True
		elif type(value)==int:
			self.setting.set_value(entry,GLib.Variant('i',value))
			return True
		elif type(value)==list:
			self.setting.set_value(entry,GLib.Variant('as',value))
			return True
		return False
		
		
	def get_value(self,entry):
		value = self.setting.get_value(entry)
		#print(entry,'->',value,'-',value.get_type_string())
		if value.get_type_string().endswith('as'):
			return self.setting.get_strv(entry)
		elif value.get_type_string().endswith('s'):
			return self.setting.get_string(entry)
		elif value.get_type_string().endswith('b'):
			return self.setting.get_boolean(entry)
		elif value.get_type_string().endswith('i'):
			return self.setting.get_int(entry)
		return None
		
	def get_values(self):
		values = []
		for entry in self.setting.list_keys():
			values.append(self.get_value(entry))
		return values
	
	def get_children(self):
		print(self.setting.list_children())
'''

	def get_dirs(self,key):
		directories = []
		for directory in self.client.all_dirs(key):
			 directories.append(directory)
		return directories
	def add_directory(self,key,directory):
		if not key.endswith('/'):
			key += '/'+directory
		else:
			key += directory
		self.set_value(key,'')
		
	def has_dirs(self,key):
		return len(self.client.all_dirs(key))>0
		
	def get_dirs_recursive(self,key):
		directories = []
		for directory in self.client.all_dirs(key):
			 directories.append(directory)			 
			 if self.has_dirs(directory):
				 directories+=self.get_dirs_recursive(directory)
		return directories
		
	def get_keys_recursive(self,key):		
		keys = []
		for directory in self.get_dirs_recursive(key):
			keys+=self.get_keys_recursive(directory)
		return keys
		
	def get_value(self,key):
		gval = self.client.get(key)
		if gval == None:
			return None
		if gval.type == GConf.ValueType.LIST:
			string_list = [item.get_string() for item in gval.get_list()]
			return string_list
		else:
			return CASTSFROM[gval.type](gval)
			
	def set_value(self,key,value):
		if type(value) in (list, tuple, set):
			string_value = [str(item) for item in value]
			CASTSTO[type(value)](self.client, key,
				GConf.ValueType.STRING, string_value)
		else:
			CASTSTO[type(value)](self.client, key, 
				value)
'''
if __name__ == '__main__':
	dcm = DConfManager('org.gnome.settings-daemon.plugins.media-keys')
	values = dcm.get_value('custom-keybindings')
	if '/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/touchpad-indicator/' in values:
		values.remove('/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/touchpad-indicator/')
		dcm.set_value('custom-keybindings',values)
	else:
		values.append('/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/touchpad-indicator/')
		dcm.set_value('custom-keybindings',values)
	dcm = DConfManager('org.gnome.settings-daemon.plugins.media-keys.custom-keybindings.touchpad-indicator')
	dcm.get_keys()
	print(dcm.set_value('binding','<Primary><Alt>p'))
	print(dcm.set_value('command','/usr/bin/python3 /home/atareao_r/Dropbox/tp/raring/touchpad-indicator/src/change_touchpad_state.py'))
	print(dcm.set_value('name','Touchpad-Indicator'))
	'''
	dcm = DConfManager('org.gnome.desktop.wm.keybindings')
	print(dcm.get_keys())
	print(dcm.get_values())
	dcm = DConfManager('org.gnome.desktop.wm.preferences')
	print(dcm.get_keys())
	print(dcm.get_values())
	#dcm.set_value('audible-bell',True)
	dcm = DConfManager('org.gnome.settings-daemon.plugins.media-keys')
	print(dcm.get_keys())
	dcm.get_children()
	'''
	'''
	def get_shortcuts():		
		gcm = GConfManager()
		print(gcm.get_keys('/org/gnome/desktop/wm/keybindings/activate-window-menu'))
		keys = []
		keys+=gcm.get_keys('/apps/compiz/general/allscreens/options')
		keys+=gcm.get_keys('/apps/metacity/global_keybindings')
		keys+=gcm.get_keys('/apps/metacity/window_keybindings')
		for directory in gcm.get_dirs('/desktop/gnome/keybindings'):
			for key in gcm.get_keys(directory):
				if key.endswith('/binding'):
					keys.append(key)
		values = []
		for key in keys:
			value = gcm.get_value(key)
			if value != 'disabled':
				values.append(value)
		return values
	print(get_shortcuts())
	gcm = GConfManager()
	gcm.set_value('/desktop/gnome/keybindings/touchpad-indicator/action','')
	gcm.set_value('/desktop/gnome/keybindings/touchpad-indicator/binding','')
	gcm.set_value('/desktop/gnome/keybindings/touchpad-indicator/name','')
	'''
