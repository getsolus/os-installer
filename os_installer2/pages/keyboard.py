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

        self.language = info[2]
        self.country = info[3]

        self.extras = info[4]

        print("Made a %s %s %s %s" % (info[1], info[2], info[3], info[4]))

        self.set_property("margin", 10)

        lab.set_text(self.dname)
        self.pack_start(lab, True, True, 0)

        preview = Gtk.Label("<a href=\"preview\">%s</a>" % "Preview")
        preview.connect("activate-link", self.on_link_activate)
        preview.set_use_markup(True)
        self.pack_end(preview, False, False, 0)

        self.show_all()


class InstallerKeyboardPage(BasePage):
    """ Basic location detection page. """

    layouts = None
    info = None
    had_init = False
    xkb = None
    shown_layouts = None

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

    def init_view(self):
        """ Initialise ourself from GNOME XKB """
        if self.had_init:
            return
        self.had_init = True
        self.xkb = GnomeDesktop.XkbInfo()

    
        items = GnomeDesktop.parse_locale(self.info.locale)
        if items[0]:
            lang = items[1];
            country = items[2]
            print(items[3])
            print(items[4])
        else:
            # Shouldn't ever happen, but ya never know.
            lang = "en"
            country = "US"
        print("Grabbing for %s %s %s" % (lang, country, self.info.locale))

        l = self.info.locale
        success, type_, id_ = GnomeDesktop.get_input_source_from_locale(l)

        kbset = set()
        kbset.update(self.xkb.get_layouts_for_country(country))
        kbset.update(self.xkb.get_layouts_for_language(lang))

        major_layouts = self.xkb.get_all_layouts()
        for item in major_layouts:
            xkbinf = self.xkb.get_layout_info(item)
            if not xkbinf[0]:
                continue
            if xkbinf[3].lower() == country.lower():
                kbset.add(item)

        layouts = list()
        for x in kbset:
            info = self.xkb.get_layout_info(x)
            if not info[0]:
                continue
            widget = KbLabel(x, info)
            layouts.append(widget)

        native = filter(lambda x: x.country.lower() == country.lower(), layouts)

        primary = None

        if not native:
            native = layouts
            for item in native:
                if item.layout[:2].lower() == lang.lower() and not item.extras:
                    print("Primary set" + item.sname)
                    primary = item
        else:
            for item in native:
                if not item.extras:
                    primary = item
                    break

        if not primary:
            print("Options: %s" % self.xkb.get_layouts_for_language(lang))
        else:
            print("Primary keyboard should be %s" % primary.dname)

        def append_inner(layout, item):
            if layout in self.shown_layouts:
                return
            self.shown_layouts.add(layout)
            self.layouts.add(item)

        self.shown_layouts = set()
        if primary:
            append_inner(primary.kb, primary)
        for item in native:
            append_inner(item.kb, item)

    def init_remaining(self):
        layouts = self.xkb.get_all_layouts()

        appends = list()
        for layout in layouts:
            # Don't dupe
            if layout in self.shown_layouts:
                continue
            info = self.xkb.get_layout_info(layout)
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

    def prepare(self, info):
        self.info = info
        print("Catering view based on %s" % self.info.locale)
        self.init_view()
