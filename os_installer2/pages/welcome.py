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

from gi.repository import Gtk
from os_installer2 import join_resource_path as jrp


class InstallerWelcomePage(Gtk.EventBox):

    def __init__(self):
        Gtk.EventBox.__init__(self)

        self.grid = Gtk.Grid()
        self.grid.set_row_spacing(32)
        self.grid.set_column_spacing(32)
        self.add(self.grid)

        # TODO: Stuff this into CSS
        label = Gtk.Label.new("<span font=\"20.5\">%s</span>" % "Welcome")
        label.set_margin_top(20)
        label.get_style_context().add_class("dim-label")
        label.set_use_markup(True)
        self.grid.attach(label, 0, 0, 2, 1)

        self.set_halign(Gtk.Align.CENTER)

        self.set_margin_top(20)
        self.set_margin_bottom(20)

        # Install
        img = Gtk.Image.new_from_file(jrp("install-solus-192-arc-style.png"))
        button = Gtk.Button()
        button.get_style_context().add_class("flat")
        button.add(img)
        self.grid.attach(button, 0, 1, 1, 1)
        # Install label
        label = Gtk.Label.new("<big>%s</big>" % "Install Solus")
        label.get_style_context().add_class("dim-label")
        label.set_use_markup(True)
        self.grid.attach(label, 0, 2, 1, 1)

        # Continue
        img = Gtk.Image.new_from_file(jrp("livepreview-192-arc-style.png"))
        button = Gtk.Button()
        button.add(img)
        button.get_style_context().add_class("flat")
        self.grid.attach(button, 1, 1, 1, 1)
        # Continue label
        label = Gtk.Label.new("<big>%s</big>" % "Continue using live preview")
        label.get_style_context().add_class("dim-label")
        label.set_use_markup(True)
        self.grid.attach(label, 1, 2, 1, 1)

        # Construct the buttons
