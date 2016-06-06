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
from .basepage import BasePage


class InstallerWelcomePage(BasePage):

    owner = None

    def __init__(self, owner):
        BasePage.__init__(self)

        self.grid = Gtk.Grid()
        self.grid.set_row_spacing(32)
        self.grid.set_column_spacing(64)
        self.add(self.grid)

        self.owner = owner

        self.set_halign(Gtk.Align.FILL)
        self.grid.set_halign(Gtk.Align.CENTER)
        self.grid.set_valign(Gtk.Align.CENTER)

        self.grid.set_margin_bottom(20)

        # Install
        img = Gtk.Image.new_from_file(jrp("install-solus-192-arc-style.png"))
        button = Gtk.Button()
        button.connect("clicked", self.on_install_clicked)
        button.get_style_context().add_class("flat")
        button.add(img)
        self.grid.attach(button, 0, 1, 1, 1)
        # Install label
        label = Gtk.Label.new("<big>{}</big>\n<small>{}</small>".format(
          "Install Solus to disk",
          "Permanently use Solus on your device"))
        label.get_style_context().add_class("dim-label")
        label.set_use_markup(True)
        self.grid.attach(label, 0, 2, 1, 1)

        # Continue
        img = Gtk.Image.new_from_file(jrp("livepreview-192-arc-style.png"))
        button = Gtk.Button()
        button.connect("clicked", self.on_return_clicked)

        button.add(img)
        button.get_style_context().add_class("flat")
        self.grid.attach(button, 1, 1, 1, 1)
        # Continue label
        label = Gtk.Label.new("<big>{}</big>\n<small>{}</small>".format(
          "Continue using live preview",
          "No changes will be made to your system"))
        label.get_style_context().add_class("dim-label")
        label.set_use_markup(True)
        self.grid.attach(label, 1, 2, 1, 1)

    def on_install_clicked(self, btn, udata=None):
        """ Start the installer fully """
        self.owner.phase_install()

    def on_return_clicked(self, btn, udata=None):
        """ Continue live session """
        self.owner.phase_live()

    def get_icon_name(self):
        return "start-here-solus"

    def get_name(self):
        return "welcome"

    def get_title(self):
        return "Install Solus"
