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
from gi.repository import Gtk


class InstallerLocationPage(BasePage):
    """ Basic location detection page. """

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
        checkbox = Gtk.CheckButton.new_with_label(check_str)
        self.pack_start(checkbox, False, False, 0)
        checkbox.set_margin_top(40)
        checkbox.set_margin_start(32)

    def get_title(self):
        return "Where are you?"

    def get_name(self):
        return "location"

    def get_icon_name(self):
        return "find-location-symbolic"
