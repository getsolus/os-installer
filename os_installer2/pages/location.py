# coding=utf-8
#
#  This file is part of os-installer
#
#  Copyright 2013-2020 Solus <copyright@getsol.us>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#

from gi.repository import Gtk

from .basepage import BasePage


class InstallerLocationPage(BasePage):
    """ Basic location detection page. """

    info = None
    checkbox = None

    def __init__(self):
        BasePage.__init__(self)

        lab = Gtk.Label("The next few questions relate to your location. To \
speed things up, the installer can perform a quick check to detect where you \
are in the world and proceed automatically.")
        lab.set_property("xalign", 0.0)
        lab.set_margin_top(40)

        lab.set_margin_start(32)

        lab.set_line_wrap(True)
        self.pack_start(lab, False, False, 0)

        check_str = "Find my location automatically."
        self.checkbox = Gtk.CheckButton.new_with_label(check_str)
        self.pack_start(self.checkbox, False, False, 0)
        self.checkbox.set_margin_top(40)
        self.checkbox.set_margin_start(32)

        self.checkbox.connect("toggled", self.on_toggled)

    def on_toggled(self, w, d=None):
        if not self.info:
            return
        self.info.enable_geoip = w.get_active()

    def get_title(self):
        return "Where are you?"

    def get_sidebar_title(self):
        return "Location"

    def get_name(self):
        return "location"

    def get_icon_name(self, plasma=False):
        if plasma:
            return "applications-internet"
        return "maps"

    def prepare(self, info):
        self.info = info
        if self.info.cached_timezone:
            self.checkbox.set_sensitive(False)
            self.checkbox.set_tooltip_text("Location already found")
