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
from gi.repository import Gdk, Gtk
import parted
import threading


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


class InstallerDiskLocationPage(BasePage):
    """ Disk location selection. """

    had_init = False
    spinner = None

    def __init__(self):
        BasePage.__init__(self)

        self.spinner = Gtk.Spinner()

        # self.pack_start(self.spinner, True, True, 0)
        self.spinner.set_halign(Gtk.Align.CENTER)
        self.spinner.set_valign(Gtk.Align.CENTER)

        self.whoops = WhoopsPage()
        self.pack_start(self.whoops, True, True, 0)

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
        dm.scan_parts()

        perms.up_permissions()
        for item in dm.devices:
            disk = None
            try:
                p = parted.getDevice(item)
                disk = parted.Disk(p)
            except Exception as e:
                print("Cannot probe disk: {}".format(e))
                continue
            if not disk:
                continue
            print("Got disk of type: {}".format(disk.type))
            sz = dm.get_disk_size_string(disk)
            dString = "{} {}".format(dm.get_disk_vendor(item),
                                     dm.get_disk_model(item))
            print("Disk: {} {}".format(dString, sz))
        print("Debug: {}".format(" ".join(dm.devices)))
        perms.down_permissions()

        # Currently the only GTK call here
        Gdk.threads_enter()
        self.info.owner.set_can_previous(True)
        # self.spinner.stop()
        Gdk.threads_leave()

    def init_view(self):
        """ Prepare for viewing... """
        if self.had_init:
            return
        self.spinner.start()
        self.had_init = True
        self.info.owner.set_can_previous(False)

        t = threading.Thread(target=self.load_disks)
        t.daemon = True
        t.start()

    def prepare(self, info):
        self.info = info
        self.init_view()
