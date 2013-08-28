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


''' Helper function '''

class InstallerSection(Gtk.VBox):

    def __init__(self):
        Gtk.VBox.__init__(self)
        self.set_border_width(10)

        # Navigation buttons
        btnbox = Gtk.ButtonBox()
        btnbox.set_layout(Gtk.ButtonBoxStyle.END)

        back = Gtk.Button(_("Previous"))
        back.set_sensitive(False)
        image = Gtk.Image()
        image.set_from_icon_name("go-previous-symbolic", Gtk.IconSize.BUTTON)
        back.set_image(image)
        btnbox.add(back)

        forward = Gtk.Button(_("Next"))
        forward_image = Gtk.Image()
        forward_image.set_from_icon_name("go-next-symbolic", Gtk.IconSize.BUTTON)
        forward.set_image(forward_image)
        btnbox.add(forward)
        
        self.pack_end(btnbox, False, False, 0)
