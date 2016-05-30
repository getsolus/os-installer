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

class MainWindow(Gtk.ApplicationWindow):

    def __init__(self, app):
        Gtk.ApplicationWindow.__init__(self, application=app)

        headerbar = Gtk.HeaderBar()
        headerbar.set_show_close_button(True)
        self.set_titlebar(headerbar)

        self.set_title("Installer")

        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_default_size(800, 600)

        self.show_all()
