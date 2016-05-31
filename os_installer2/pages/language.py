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


class LcLabel(Gtk.Label):
    """ View label for locales, save code duping """

    lc_code = None
    untransl = None

    def __init__(self, lc_code):
        Gtk.Label.__init__(self)
        self.set_text(lc_code)
        self.set_halign(Gtk.Align.START)
        self.lc_code = lc_code

        # transl = GnomeDesktop.get_language_from_locale(lc_code, lc_code)
        untransl = GnomeDesktop.get_language_from_locale(lc_code, None)
        self.set_property("margin", 10)

        self.dname = untransl

        self.set_text(untransl)

        self.show()


class InstallerLanguagePage(BasePage):
    """ Basic language page. """

    # Scrollbox
    scroll = None

    # Main content
    listbox = None

    def __init__(self):
        BasePage.__init__(self)

        self.scroll = Gtk.ScrolledWindow(None, None)
        self.scroll.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        self.scroll.set_border_width(40)
        self.add(self.scroll)

        self.listbox = Gtk.ListBox()
        self.scroll.add(self.listbox)
        self.scroll.set_halign(Gtk.Align.CENTER)

        # Fix up policy
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.init_view()

    def init_view(self):
        """ Do the hard work of actually setting up the view """
        locales = sorted(GnomeDesktop.get_all_locales())
        appends = list()
        for lc in locales:
            item = LcLabel(lc)
            appends.append(item)
        appends.sort(key=lambda x: x.dname.lower())
        for item in appends:
            self.listbox.add(item)

    def get_title(self):
        return "Choose a language"

    def get_name(self):
        return "language"

    def get_icon_name(self):
        return "preferences-desktop-locale-symbolic"
