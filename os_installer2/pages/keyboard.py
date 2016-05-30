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
from gi.repository import Gtk


class InstallerKeyboardPage(BasePage):
    """ Basic location detection page. """

    tview_layouts = None
    tview_variants = None

    def __init__(self):
        BasePage.__init__(self)

        # Hold everything up in a grid
        grid = Gtk.Grid()
        self.pack_start(grid, True, True, 0)
        grid.set_column_spacing(6)
        grid.set_row_spacing(6)
        grid.set_margin_start(32)

        # Init main layouts view
        self.tview_layouts = Gtk.TreeView()
        scroll = Gtk.ScrolledWindow(None, None)
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.tview_layouts)
        scroll.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        scroll.set_hexpand(True)
        scroll.set_vexpand(True)
        grid.attach(scroll, 0, 0, 1, 1)

        # Variants view
        self.tview_variants = Gtk.TreeView()
        scroll = Gtk.ScrolledWindow(None, None)
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.tview_variants)
        scroll.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        scroll.set_hexpand(True)
        scroll.set_vexpand(True)
        grid.attach(scroll, 1, 0, 1, 1)

        # Input tester
        inp_entry = Gtk.Entry()
        t_str = "Type here to test your keyboard layout"
        inp_entry.set_placeholder_text(t_str)

        grid.attach(inp_entry, 0, 1, 2, 1)

    def get_title(self):
        return "Choose a keyboard layout"

    def get_name(self):
        return "keyboard"

    def get_icon_name(self):
        return "input-keyboard-symbolic"
