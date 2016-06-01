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
from gi.repository import Gdk, Gtk, GLib
from os_installer2.diskman import DriveProber
import threading


class ChooserPage(Gtk.VBox):
    """ Main chooser UI """

    combo = None

    def __init__(self):
        Gtk.VBox.__init__(self)
        self.set_border_width(40)

        # set up the disk selector
        self.combo = Gtk.ComboBoxText()

        self.pack_start(self.combo, False, False, 0)


class WhoopsPage(Gtk.VBox):
    """ No disks on this system """

    def __init__(self):
        Gtk.VBox.__init__(self)

        img = Gtk.Image.new_from_icon_name("face-crying-symbolic",
                                           Gtk.IconSize.DIALOG)

        self.pack_start(img, False, False, 10)

        label = Gtk.Label("<big>%s</big>" %
                          "Oh no! Your system has no disks available.\n"
                          "There is nowhere to install Solus.")
        label.set_property("xalign", 0.5)
        label.set_use_markup(True)
        self.pack_start(label, False, False, 10)

        self.set_valign(Gtk.Align.CENTER)
        self.set_halign(Gtk.Align.CENTER)


class LoadingPage(Gtk.HBox):
    """ Spinner/load box """

    def __init__(self):
        Gtk.HBox.__init__(self)

        self.spinner = Gtk.Spinner()
        self.pack_start(self.spinner, False, False, 10)

        self.label = Gtk.Label("Examining local storage devices" + u"…")
        self.pack_start(self.label, False, False, 10)

        self.set_valign(Gtk.Align.CENTER)
        self.set_halign(Gtk.Align.CENTER)

    def start(self):
        self.spinner.start()

    def stop(self):
        self.spinner.stop()


class InstallerDiskLocationPage(BasePage):
    """ Disk location selection. """

    had_init = False
    spinner = None

    stack = None
    whoops = None
    chooser = None
    prober = None

    def __init__(self):
        BasePage.__init__(self)

        self.stack = Gtk.Stack()
        self.pack_start(self.stack, True, True, 0)

        self.spinner = LoadingPage()

        self.whoops = WhoopsPage()
        self.stack.add_named(self.whoops, "whoops")
        self.stack.add_named(self.spinner, "loading")
        self.chooser = ChooserPage()
        self.stack.add_named(self.chooser, "chooser")

        self.stack.set_visible_child_name("loading")

    def get_title(self):
        return "Where should we install?"

    def get_name(self):
        return "disk-location"

    def get_icon_name(self):
        return "drive-harddisk-system-symbolic"

    def load_disks(self):
        """ Load the disks within a thread """
        # Scan parts
        dm = self.info.owner.get_disk_manager()
        perms = self.info.owner.get_perms_manager()

        perms.up_permissions()
        self.prober = DriveProber(dm)
        self.prober.probe()
        perms.down_permissions()

        # Currently the only GTK call here
        Gdk.threads_enter()
        self.info.owner.set_can_previous(True)
        if len(self.prober.drives) == 0:
            # No drives
            self.stack.set_visible_child_name("whoops")
        else:
            # Let them choose
            self.stack.set_visible_child_name("chooser")
        self.spinner.stop()
        Gdk.threads_leave()

        GLib.idle_add(self.update_disks)

    def update_disks(self):
        """ Thread load finished, update UI from discovered info """
        self.chooser.combo.remove_all()
        for drive in self.prober.drives:
            print("Debug: Add device: {}".format(drive.path))
            for os_path in drive.operating_systems:
                os = drive.operating_systems[os_path]
                print("\t{} OS: {} (icon: {})".format(os_path,
                                                      os.name, os.icon_name))
            self.chooser.combo.append_text(drive.get_display_string())
        self.chooser.combo.set_active(0)
        if self.prober.is_broken_windows_uefi():
            print("Broken UEFI system detected")
        else:
            print("UEFI in good order")
        return False

    def init_view(self):
        """ Prepare for viewing... """
        if self.had_init:
            return
        self.stack.set_visible_child_name("loading")
        self.spinner.start()
        self.spinner.show_all()
        self.had_init = True
        self.info.owner.set_can_previous(False)

        t = threading.Thread(target=self.load_disks)
        t.daemon = True
        t.start()

    def prepare(self, info):
        self.info = info
        self.init_view()
