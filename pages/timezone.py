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
from basepage import BasePage
from widgets.tz import Database, Location

class TimezonePage(BasePage):

    def __init__(self):
        BasePage.__init__(self)
        #self.set_border_width(30)
        self.map = TimezoneMap.TimezoneMap()
        self.map.connect("location-changed", self.changed)
        self.pack_start(self.map, True, True, 0)

        # Set up timezone database
        self.db = Database()
        self.map.set_timezone("Europe/London")

        self.locations = Gtk.Entry()
        self.locations.set_placeholder_text(_("Search for your timezone..."))

        tz_model = Gtk.ListStore(str,str,str,str,float,float,str)

        for item in self.db.locations:
            tz_model.append([item.human_zone, item.human_country,  None, item.country, item.longitude, item.latitude,item.zone])

        completion = TimezoneMap.TimezoneCompletion()
        completion.set_model(tz_model)
        completion.set_text_column(0)
        completion.set_inline_completion(True)
        completion.set_inline_selection(True)
        completion.connect("match-selected", self.change_timezone)
        self.locations.set_completion(completion)

        self.pack_end(self.locations, False, False, 3)

    def change_timezone(self, completion, model, selection):
        item = model[selection]
        zone = item[6]
        self.map.set_timezone(zone)

    def changed(self, map, location):
        zone = location.get_property("zone")
        nice_loc = self.db.tz_to_loc[zone]

        self.map.set_watermark("%s (%s)" % (nice_loc.human_zone, nice_loc.human_country))

    def get_title(self):
        return _("Choose your timezone")

    def get_name(self):
        return "timezone"

    def get_icon_name(self):
        return "preferences-system-time-symbolic"
