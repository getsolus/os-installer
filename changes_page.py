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

    def __init__(self, owner):
        Gtk.VBox.__init__(self)

        view = WebKit.WebView()
        view.set_transparent(True)
        # Eventually need to open a local changes file from real location
        lines = None
        base_uri = "file:///usr/share/os-installer/changes/"
        with open ("changes/index.html", "r") as html:
            lines = "\n".join(html.readlines())

        view.load_html_string(lines, base_uri)

        settings = WebKit.WebSettings()
        settings.set_property("enable_file_access_from_file_uris", True)
        view.set_settings(settings)
        self.title = Gtk.Label("<span font=\"20.5\" color=\"#82807b\">%s</span>" % _("Changes"))
        self.title.set_use_markup(True)

        self.image = Gtk.Image()
        self.image.set_from_icon_name("learnmore-symbolic", Gtk.IconSize.DIALOG)
        self.image.set_padding(10, 10)

        header = Gtk.HBox()
        header.pack_start(self.image, False, False, 0)
        header.pack_start(self.title, False, False, 0)
        self.pack_start(header, False, False, 3)

        # We need a way to go back to the main window.. :)
        self.back = Gtk.Button()
        back_image = Gtk.Image()
        back_image.set_from_icon_name("go-home-symbolic", Gtk.IconSize.BUTTON)
        self.back.set_image(back_image)
        self.back.set_relief(Gtk.ReliefStyle.NONE)
        self.back.connect("clicked", lambda x: owner.go_home())

        header.pack_end(self.back, False, False, 0)

        scroller = Gtk.ScrolledWindow(None, None)
        scroller.add(view)
        scroller.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        self.pack_start(scroller, True, True, 0)

        # Add content
