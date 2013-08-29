#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  changes_page.py - Whats new, etc
#  
#  Copyright 2013 Ikey Doherty <ikey@solusos.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#
import gi.repository
from gi.repository import Gtk, TimezoneMap
import os      

        
class TimezonePage(Gtk.VBox):

    def __init__(self):
        Gtk.VBox.__init__(self)
        #self.set_border_width(30)
        self.map = TimezoneMap.TimezoneMap()
        self.pack_start(self.map, True, True, 0)

    def get_title(self):
        return _("Choose your timezone")

    def get_name(self):
        return "timezone"

    def get_icon_name(self):
        return "preferences-system-time-symbolic"
