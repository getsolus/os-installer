#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  summary.py - Installation options summary
#  
#  Copyright 2013 Ikey Doherty <ikey@solusos.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#
import gi.repository
from gi.repository import Gtk
from basepage import BasePage

from installer import Setup, InstallerEngine

class InstallationPage(BasePage):

    def __init__(self, installer):
        BasePage.__init__(self)

        self.label = Gtk.Label("")
        self.progress = Gtk.ProgressBar()

        self.pack_end(self.label, False, False, 0)
        self.pack_end(self.progress, False, False, 0)
        
        self.installer = installer
        self.engine = InstallerEngine()

        self.setup = Setup()

    def prepare(self, pages=None):
        self.installer.can_go_back(False)
        self.installer.can_go_forward(False)

        for page in pages:
            page.seed(self.setup)
        print "Seeded"
        self.setup.print_setup()

    def get_title(self):
        return _("Installing")

    def get_name(self):
        return "installing"

    def get_icon_name(self):
        return "system-software-install-symbolic"

    def is_hidden(self):
        return True
