#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  installer_section.py - Holds installer pages
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
from gi.repository import Gtk, Gdk, Pango
from resources import *

from pages.language import LanguagePage
from pages.timezone import TimezonePage

class InstallerSection(Gtk.VBox):

    def __init__(self):
        Gtk.VBox.__init__(self)
        self.set_border_width(10)

        # Title
        self.title = Gtk.Label("")
        self.title.set_use_markup(True)

        self.image = Gtk.Image()
        self.image.set_padding(10, 10)

        header = Gtk.HBox()
        header.pack_start(self.image, False, False, 0)
        header.pack_start(self.title, False, False, 0)

        self.pack_start(header, False, True, 10)
        
        # Content area
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.pack_start(self.stack, True, True, 0)

        self.index = 0
        self.selected_page = 0
        self.pages = dict()
        self._add_page(LanguagePage())
        self._add_page(TimezonePage())

        # Navigation buttons
        btnbox = Gtk.ButtonBox()
        btnbox.set_layout(Gtk.ButtonBoxStyle.END)
        btnbox.set_margin_top(10)

        back = Gtk.Button(_("Previous"))
        back.connect("clicked", self.nav, False)
        #back.set_sensitive(False)
        image = Gtk.Image()
        image.set_from_icon_name("go-previous-symbolic", Gtk.IconSize.BUTTON)
        back.set_image(image)
        btnbox.add(back)

        forward = Gtk.Button(_("Next"))
        forward.connect("clicked", self.nav, True)
        forward_image = Gtk.Image()
        forward_image.set_from_icon_name("go-next-symbolic", Gtk.IconSize.BUTTON)
        forward.set_image(forward_image)
        btnbox.add(forward)

        self._select_page(0)
        self.pack_end(btnbox, False, False, 0)

    def nav(self, btn, forward=False):
        index = self.selected_page + 1 if forward else self.selected_page - 1
        print index
        self._select_page(index)

    def _select_page(self, index):
        page = self.pages[index]
        self.title.set_markup("<span font=\"20.5\" color=\"#82807b\">%s</span>" % page.get_title())
        self.image.set_from_icon_name(page.get_icon_name(), Gtk.IconSize.DIALOG)
        self.stack.set_visible_child_name(page.get_name())
        self.selected_page = index

    def _add_page(self, page):
        self.pages[self.index] = page
        self.stack.add_named(page, page.get_name())
        self.index += 1

