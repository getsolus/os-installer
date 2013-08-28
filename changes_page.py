#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  changes_page.py - Whats new, etc
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
from gi.repository import Gtk, WebKit


class ChangesPage(Gtk.VBox):

    def __init__(self):
        Gtk.VBox.__init__(self)

        view = WebKit.WebView()
        view.set_transparent(True)
        # Eventually need to open a local changes file
        view.open("http://solusos.com")

        label = "<span font=\"40.5\" color=\"#82807b\">%s</span>" % _("Changes")
        label_wid = Gtk.Label(label)
        label_wid.set_use_markup(True)
        self.pack_start(label_wid, False, False, 3)

        scroller = Gtk.ScrolledWindow(None, None)
        scroller.add(view)
        self.pack_start(scroller, True, True, 0)

        # Add content
