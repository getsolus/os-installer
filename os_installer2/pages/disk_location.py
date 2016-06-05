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
from os_installer2.strategy import DiskStrategyManager
import threading


class ChooserPage(Gtk.VBox):
    """ Main chooser UI """

    combo = None
    strategy_box = None
    respond = False
    manager = None
    drives = None

    def __init__(self):
        Gtk.VBox.__init__(self)
        self.set_border_width(40)

        # set up the disk selector
        self.combo = Gtk.ComboBoxText()

        self.pack_start(self.combo, False, False, 0)

        self.strategy_box = Gtk.VBox(0)
        self.strategy_box.set_margin_top(20)
        self.pack_start(self.strategy_box, True, True, 0)

        self.respond = True
        self.combo.connect("changed", self.on_combo_changed)

    def on_combo_changed(self, combo, w=None):
        if not self.respond:
            return
        print("Selected: {}".format(combo.get_active_id()))
        drive = self.drives[combo.get_active_id()]
        strats = self.manager.get_strategies(drive)

        print("Got {} strategies for {}".format(len(strats), drive.path))

        self.reset_options()
        leader = None
        for strat in strats:
            button = Gtk.RadioButton.new_with_label_from_widget(
                leader, strat.get_display_string())
            if not leader:
                leader = button
            button.get_child().set_use_markup(True)
            self.strategy_box.pack_start(button, False, False, 8)
            button.show_all()

    def reset_options(self):
        for widget in self.strategy_box.get_children():
            widget.destroy()

    def reset(self):
        self.respond = False
        self.drives = dict()
        self.combo.remove_all()
        self.reset_options()
        self.respond = True

    def set_drives(self, prober):
        """ Set the display drives """
        self.reset()

        self.manager = DiskStrategyManager(prober)
        active_id = None
        for drive in prober.drives:
            self.combo.append(drive.path, drive.get_display_string())
            self.drives[drive.path] = drive
            if not active_id:
                active_id = drive.path
        self.combo.set_active_id(active_id)


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
        self.chooser.set_drives(self.prober)
        for drive in self.prober.drives:
            print("Debug: Add device: {}".format(drive.path))
            for os_path in drive.operating_systems:
                os = drive.operating_systems[os_path]
                print("\t{} OS: {} (icon: {})".format(os_path,
                                                      os.name, os.icon_name))
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
