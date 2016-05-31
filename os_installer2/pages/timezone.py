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
        self.frame = Gtk.AspectFrame()
        self.frame.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        self.tmap = TimezoneMap.TimezoneMap()
        self.pack_start(self.frame, True, True, 0)
        self.frame.set_margin_end(20)
        self.frame.set_margin_start(20)
        self.frame.add(self.tmap)

        self.locations = Gtk.Entry()
        self.locations.set_margin_end(10)
        self.locations.set_margin_top(10)
        self.locations.set_margin_end(35)
        self.locations.set_margin_start(35)
        self.pack_end(self.locations, False, False, 0)

    def get_title(self):
        return "Choose your timezone"

    def get_name(self):
        return "timezone"

    def get_icon_name(self):
        return "preferences-system-time-symbolic"
