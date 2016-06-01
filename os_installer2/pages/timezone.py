#!/bin/true
# -*- coding: utf-8 -*-
#
#  This file is part of os-installer
#
#  Copyright 2013-2016 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#

from .basepage import BasePage

from gi.repository import TimezoneMap, Gtk


class InstallerTimezonePage(BasePage):
    """ timezone setup page. """

    tmap = None
    locations = None

    def __init__(self):
        BasePage.__init__(self)
        self.frame = Gtk.Frame()
        self.frame.set_shadow_type(Gtk.ShadowType.NONE)
        self.tmap = TimezoneMap.TimezoneMap()
        self.pack_start(self.frame, True, True, 0)
        self.frame.set_margin_end(0)
        self.frame.set_margin_start(0)
        self.frame.add(self.tmap)

        self.locations = Gtk.Entry()
        self.locations.set_property("margin-right", 30)
        self.locations.set_property("margin-start", 30)
        self.locations.set_property("margin-top", 10)
        self.pack_end(self.locations, False, False, 0)

    def get_title(self):
        return "Choose your timezone"

    def get_name(self):
        return "timezone"

    def get_icon_name(self):
        return "preferences-system-time-symbolic"
