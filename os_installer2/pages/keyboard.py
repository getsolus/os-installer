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

from .basepage import BasePage
from gi.repository import Gtk, GnomeDesktop


class KbLabel(Gtk.HBox):
    """ View label for locales, save code duping """

    kb = None
    dname = None

    def on_link_activate(self, lbl, udata=None):
        # Consume link
        return True

    def __init__(self, kb, info):
        Gtk.HBox.__init__(self)
        self.kb = kb

        lab = Gtk.Label("")
        lab.set_halign(Gtk.Align.START)

        self.dname = info[1]
        self.sname = info[2]
        self.layout = info[3]
        self.variant = info[4]

        self.set_property("margin", 10)

        lab.set_text(self.dname)
        self.pack_start(lab, True, True, 0)

        preview = Gtk.Label("<a href=\"preview\">%s</a>" % "Preview")
        preview.connect("activate-link", self.on_link_activate)
        preview.set_use_markup(True)
        self.pack_end(preview, False, False, 0)

        self.show()


class InstallerKeyboardPage(BasePage):
    """ Basic location detection page. """

    layouts = None

    def __init__(self):
        BasePage.__init__(self)

        # Hold everything up in a grid
        grid = Gtk.Grid()
        self.pack_start(grid, True, True, 0)
        grid.set_column_spacing(6)
        grid.set_row_spacing(6)
        grid.set_margin_start(32)
        grid.set_halign(Gtk.Align.CENTER)

        # Init main layouts view
        self.layouts = Gtk.ListBox()
        scroll = Gtk.ScrolledWindow(None, None)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.layouts)
        scroll.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        scroll.set_vexpand(True)
        grid.attach(scroll, 0, 0, 2, 1)

        self.layouts.set_size_request(500, -1)

        # Input tester
        inp_entry = Gtk.Entry()
        t_str = "Type here to test your keyboard layout"
        inp_entry.set_placeholder_text(t_str)

        grid.attach(inp_entry, 0, 1, 2, 1)

        self.init_view()

    def init_view(self):
        """ Initialise ourself from GNOME XKB """
        xkb = GnomeDesktop.XkbInfo()
        layouts = xkb.get_all_layouts()

        appends = list()
        for layout in layouts:
            info = xkb.get_layout_info(layout)
            success = info[0]
            if not success:
                continue

            widget = KbLabel(layout, info)
            appends.append(widget)
        appends.sort(key=lambda x: x.dname.lower())
        for app in appends:
            self.layouts.add(app)

    def get_title(self):
        return "Choose a keyboard layout"

    def get_name(self):
        return "keyboard"

    def get_icon_name(self):
        return "input-keyboard-symbolic"
