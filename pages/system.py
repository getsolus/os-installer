#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  system.py - System options
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

class SystemPage(BasePage):

    def __init__(self, installer):
        BasePage.__init__(self)
        self.installer = installer
        self.install_grub = False

        content = Gtk.VBox()
        content.set_border_width(30)
        self.add(content)
        
        # hostname section
        host = Gtk.Frame()
        host.set_label(_("What name should this computer use on the network?"))
        content.pack_start(host, False, False, 10)

        self.host_entry = Gtk.Entry()
        self.host_entry.set_placeholder_text(_("Type the hostname here"))

        host_wrap = Gtk.VBox()
        host_wrap.set_border_width(5)
        host_wrap.add(self.host_entry)
        host.add(host_wrap)

        # grub
        grub_frame = Gtk.Frame()
        grub_check = Gtk.CheckButton(_("Should we install a boot loader (GRUB) on this computer?"))
        grub_frame.set_label_widget(grub_check)

        self.grub_combo = Gtk.ComboBox()
        grub_wrap = Gtk.VBox()
        grub_wrap.set_border_width(5)
        grub_wrap.add(self.grub_combo)
        grub_frame.add(grub_wrap)

        # Hook up the checkbutton
        grub_check.connect("clicked", lambda x: self.grub_combo.set_sensitive(x.get_active()))
        self.grub_combo.set_sensitive(False)
        
        content.pack_start(grub_frame, False, False, 10)
                
        self.installer.can_go_forward(False)


    def prepare(self):
        self.installer.can_go_back(True)
        self.installer.can_go_forward(False)
        
    def get_title(self):
        return _("System settings")

    def get_name(self):
        return "system"

    def get_icon_name(self):
        return "preferences-system-symbolic"

    def get_primary_answer(self):
        return "Not yet implemented"
      
