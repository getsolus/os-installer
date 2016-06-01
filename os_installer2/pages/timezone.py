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
from os_installer2.tz import Database

from gi.repository import TimezoneMap, Gtk, Gdk


class InstallerTimezonePage(BasePage):
    """ timezone setup page. """

    tmap = None
    locations = None
    db = None

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

        self.locations.set_placeholder_text("Search for your timezone" + u"…")

        completion = TimezoneMap.TimezoneCompletion()
        completion.set_text_column(0)
        completion.set_inline_completion(True)
        completion.set_inline_selection(True)
        completion.connect("match-selected", self.change_timezone)
        self.locations.set_completion(completion)
        self.tmap.connect("location-changed", self.changed)

    def do_expensive_init(self):
        # Set up timezone database
        self.db = Database()

        tz_model = Gtk.ListStore(str, str, str, str, float, float, str)

        for item in self.db.locations:
            tz_model.append([item.human_zone, item.human_country,  None,
                             item.country, item.longitude, item.latitude,
                             item.zone])

        Gdk.threads_enter()
        self.locations.get_completion().set_model(tz_model)
        Gdk.threads_leave()

    def get_title(self):
        return "Choose your timezone"

    def get_name(self):
        return "timezone"

    def get_icon_name(self):
        return "preferences-system-time-symbolic"

    def change_timezone(self, completion, model, selection):
        item = model[selection]
        zone = item[6]
        self.tmap.set_timezone(zone)

    def changed(self, map, location):
        zone = location.get_property("zone")
        nice_loc = self.db.tz_to_loc[zone]

        self.timezone_human = "%s (%s)" % (nice_loc.human_zone,
                                           nice_loc.human_country)
        self.tmap.set_watermark(self.timezone_human)
        self.locations.set_text(nice_loc.human_zone)

        # Ok to go forward
        self.info.owner.set_can_next(True)
        self.info.timezone = zone

    def prepare(self, info):
        self.info = info
        # TODO: Seed based on geoip
        if self.info.timezone:
            self.info.owner.set_can_next(True)
        else:
            self.info.owner.set_can_next(False)
