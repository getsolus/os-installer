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
from os_installer2 import join_resource_path as jrp


class InstallationCompletePage(BasePage):
    """ Last page seen by users """

    def __init__(self):
        BasePage.__init__(self)

        box = Gtk.VBox(0)
        self.pack_start(box, True, True, 0)
        box.set_border_width(40)
        box.set_valign(Gtk.Align.CENTER)
        box.set_halign(Gtk.Align.CENTER)

        img = Gtk.Image.new_from_file(jrp("install-complete.png"))
        img.set_halign(Gtk.Align.CENTER)
        box.pack_start(img, False, False, 0)

        lab = Gtk.Label("<big>You may now exit the installer.</big>")
        lab.set_use_markup(True)
        lab.set_halign(Gtk.Align.CENTER)
        lab.set_property("xalign", 0.5)
        box.pack_start(lab, False, False, 0)
        lab.set_property("margin-top", 5)
        lab.set_property("margin-bottom", 5)

        lab = Gtk.Label("Restart and then remove any installation media to start "
                        "using your new operating system.")
        lab.set_use_markup(True)
        lab.set_halign(Gtk.Align.CENTER)
        lab.set_property("xalign", 0.5)
        box.pack_start(lab, False, False, 0)

    def get_title(self):
        return "Installation complete!"

    def get_name(self):
        return "complete"

    def get_icon_name(self):
        return "start-here-solus"
