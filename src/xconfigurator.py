#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
__author__='atareao'
__date__ ='$21/11/2010'
#
#
# Copyright (C) 2010 Lorenzo Carbonell
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



import os
import subprocess
from subprocess import Popen, PIPE


XFCONFQUERY = '/usr/bin/xfconf-query'

def xfconfquery_exists():
	return os.path.exists(XFCONFQUERY)

def get_desktop_environment():
	desktop_environment = 'generic'
	if os.environ.get('KDE_FULL_SESSION') == 'true':
		desktop_environment = 'kde'
	elif os.environ.get('GNOME_DESKTOP_SESSION_ID'):
		desktop_environment = 'gnome'
	else:
		try:
			info = getoutput('xprop -root _DT_SAVE_MODE')
			if ' = "xfce4"' in info:
				desktop_environment = 'xfce'
		except (OSError, RuntimeError):
			pass
	return desktop_environment

def getoutput(cmd):
	val = Popen(cmd, shell=True, stdout=PIPE).communicate()[0].decode("utf-8").rstrip().lstrip()
	return val

class XFCEConfiguration:
	def __init__(self, channel):
		self.channel = channel
	
	def get_keys(self):
		out = getoutput('xfconf-query -c %s -l' % self.channel)
		keys = []
		for key in out.split('\n'):
			if '\override' not in key:
				key = key.rstrip().lstrip()
				value = self.get_value(key)
				keys.append({'key':key,'value':value})
		return keys
	
	def set_property(self,property,value):
		val = getoutput('xfconf-query -c %s --create --property "%s" --set "%s" --type string'%(self.channel,property,value))
		return val
		
	def reset_property(self,property):
		val = getoutput('xfconf-query -c %s --reset --property "%s"'%(self.channel,property))
		return val

	def get_value(self,property):
		if len(property) >0 :
			val = getoutput('xfconf-query -c %s --property "%s"'%(self.channel,property))
			return val
		return None
		
	def search_for_value_in_properties_startswith(self,startswith,value):
		found_keys = []
		keys = self.search_for_property_startswith(startswith)
		for key in keys:
			if key['value'] == value:
				found_keys.append(key)
		return found_keys
			
	def search_for_property_startswith(self,startswith):
		found_keys = []
		keys = self.get_keys()
		for key in keys:
			if key['key'].startswith(startswith) and key not in found_keys:
				found_keys.append(key)
		return found_keys
if __name__=='__main__':
	if xfconfquery_exists():
		key = '<Control><Alt>t'
		xfceconf = XFCEConfiguration('xfce4-keyboard-shortcuts')
		akeys = xfceconf.search_for_value_in_properties_startswith('/commands/custom/','/usr/share/touchpad-indicator/change_touchpad_state.py')
		print('akeys: '+str(akeys))
		if akeys:
			for akey in akeys:
				print('akey: '+str(akey))
				xfceconf.reset_property(akey['key'])
		if True:
			key = key.replace('<Primary>','<Control>')
			print(key)
			print(xfceconf.set_property('/commands/custom/'+key,'/usr/share/touchpad-indicator/change_touchpad_state.py'))
	exit(0)
