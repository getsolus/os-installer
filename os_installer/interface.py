#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  interface.py - Main Installer UI
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
from live_page import LivePage
from changes_page import ChangesPage
from installer_section import InstallerSection
from resources import *


class InstallerWindow(Gtk.Window):

    def rowsel(self, box, row):
        page = self.rows[row]
        self.stack.set_visible_child_name(page)

    def go_home(self):
        self.stack.set_visible_child_name("intro")

    def __init__(self):
        Gtk.Window.__init__(self)
        self.connect("destroy", Gtk.main_quit)

        self.set_size_request (700, 500)
        self.set_position (Gtk.WindowPosition.CENTER)
        self.set_title(_("Installer"))

        self._init_theme()

        self.layout = Gtk.VBox()

        self.add(self.layout)

        self.stack = Gtk.Stack()
        self.stack.add_named(self.create_intro_page(), "intro")
        self.stack.add_named(InstallerSection(), "install")
        self.stack.add_named(LivePage(), "live")
        self.stack.add_named(ChangesPage(self), "changes")

        self.listbox.connect("row-activated", self.rowsel)
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.layout.add(self.stack)

        self.set_resizable(False)
        self.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        self.show_all()

    def _init_theme(self):
        # TEMPORARY: Needs to be read from config
        theme = config[UI_THEME]
        self.get_settings().set_string_property("gtk-icon-theme-name", theme["IconTheme"], "0")
        self.get_settings().set_string_property("gtk-theme-name", theme["Widgets"], "Adwaita")
        self.use_symbolic = theme["SymbolicIcons"].lower() == "true"

        context = self.get_style_context()
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path('%s/styling.css' % RESOURCE_DIR)
        screen = Gdk.Screen.get_default()
        context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    def create_intro_page(self):
        layout = Gtk.VBox()
        # Create a pretty label
        label = "<span font=\"40.5\" color=\"#82807b\">%s</span>" % DISTRO_NAME
        label_widg = Gtk.Label(label)
        label_widg.set_use_markup(True)

        # Release label
        release = "<span color=\"#82807b\" font=\"14.5\">%s</span>" % DISTRO_VERSION
        release_label = Gtk.Label(release)
        release_label.set_use_markup(True)
        release_label.set_angle(-30)

        header = Gtk.HBox()
        header.pack_end(release_label, False, False, 0)
        layout.pack_start(header, False, True, 0)

        layout.pack_start(label_widg, True, True, 0)        

        self.listbox = Gtk.ListBox()
        self.rows = dict()
        
        # buttons
        install = self.fancy_button(_("Install to your computer now"), "install-symbolic")
        self.listbox.add(install)
        self.rows[self.listbox.get_row_at_index(0)] = "install"

        help_icon = "learnmore-symbolic" if self.use_symbolic else "help-browser-symbolic" 
        help_btn = self.fancy_button(_("What's new in this release"), help_icon)
        self.listbox.add(help_btn)
        self.rows[self.listbox.get_row_at_index(1)] = "changes"

        live = self.fancy_button(_("Continue using the LiveCD"), "livecd-symbolic")
        self.listbox.add(live)
        self.rows[self.listbox.get_row_at_index(2)] = "live"
        
        scroller = Gtk.ScrolledWindow(None,None)
        scroller.set_border_width(5)
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)
        scroller.set_shadow_type(Gtk.ShadowType.IN)
        scroller.add(self.listbox)
        layout.pack_end(scroller, False, True, 0)

        return layout

    def fancy_button(self, text, icon_name):
        if not self.use_symbolic:
            icon_name = icon_name.replace("-symbolic", "")

        image = Gtk.Image()
        image.set_from_icon_name(icon_name, Gtk.IconSize.DIALOG)
        image.set_padding(5, 5)

        hbox = Gtk.HBox(0, 0)
        label = Gtk.Label(text)
        label.set_alignment(0.5, 0.5)
        label.set_justify(Gtk.Justification.RIGHT)
        hbox.pack_start(image, False, False, 0)
        hbox.pack_start(label, True, False, 0)
        return hbox
