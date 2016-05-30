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


class InstallerWelcomePage(Gtk.EventBox):

    def __init__(self):
        Gtk.EventBox.__init__(self)

        self.grid = Gtk.Grid()
        self.add(self.grid)

        # TODO: Stuff this into CSS
        label = Gtk.Label.new("<span font=\"20.5\">%s</span>" % "Welcome")
        label.get_style_context().add_class("dim-label")
        label.set_use_markup(True)
        self.grid.attach(label, 0, 0, 1, 1)

        self.set_halign(Gtk.Align.CENTER)

        self.set_margin_top(20)
        self.set_margin_bottom(20)
