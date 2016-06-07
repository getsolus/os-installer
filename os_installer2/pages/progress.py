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
from gi.repository import Gtk, GLib, Pango
import threading
import time


# Update 5 times a second, vs every byte copied..
UPDATE_FREQUENCY = 1000 / 5


class InstallerProgressPage(BasePage):
    """ Actual installation :o """

    info = None
    progressbar = None
    label = None
    had_start = False
    installing = False

    # Current string for the idle monitor to display in Gtk thread
    display_string = None

    def __init__(self):
        BasePage.__init__(self)

        box = Gtk.VBox(0)
        box.set_border_width(20)
        self.pack_end(box, False, False, 0)

        self.label = Gtk.Label("Initializing installer")
        self.label.set_max_width_chars(250)
        self.label.set_ellipsize(Pango.EllipsizeMode.END)
        self.label.set_halign(Gtk.Align.START)
        box.pack_start(self.label, True, True, 2)

        self.progressbar = Gtk.ProgressBar()
        box.pack_start(self.progressbar, False, False, 2)

    def get_title(self):
        return "Installing Solus"

    def get_name(self):
        return "install"

    def get_icon_name(self):
        return "install-symbolic"

    def begin_install(self):
        """ Begin the real work of doing the installation """
        # We don't yet do anything...
        self.label.set_markup("Not yet capable of installing :o")

        self.installing = True
        # Hook up the idle monitor
        GLib.timeout_add(UPDATE_FREQUENCY, self.idle_monitor)
        t = threading.Thread(target=self.install_thread)
        t.start()

    def get_display_string(self):
        """ Ensure duped access for display string (threading..) """
        return str(self.display_string)

    def set_display_string(self, sz):
        """ Set the current display string """
        self.display_string = sz

    def idle_monitor(self):
        """ Called periodicially so we can update our view """
        self.label.set_markup(self.get_display_string())
        if not self.installing:
            print("Finished idle_monitor")
        return self.installing

    def prepare(self, info):
        self.info = info
        self.info.owner.set_can_next(False)
        self.info.owner.set_can_previous(False)
        self.info.owner.set_can_quit(False)

        if not self.had_start:
            self.had_start = True
            self.begin_install()

    def install_thread(self):
        """ Handle the real work of installing =) """
        self.set_display_string("Analyzing installation configuration")

        # We didn't *really* do anything ;)
        time.sleep(3)
        self.set_display_string("Nah only kidding")
        self.installing = False
