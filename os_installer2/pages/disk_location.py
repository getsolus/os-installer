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


class BrokenWindowsPage(Gtk.VBox):
    """ Indicate to the user that they booted in the wrong mode """

    owner = None

    def __init__(self, owner):
        Gtk.VBox.__init__(self)
        self.owner = owner

        img = Gtk.Image.new_from_icon_name("face-crying-symbolic",
                                           Gtk.IconSize.DIALOG)

        self.pack_start(img, False, False, 10)

        label = Gtk.Label("<big>{}</big>".format(
                          "You have booted Solus in UEFI mode, however your\n"
                          "system is configured by Windows to use BIOS mode.\n"
                          "If you wish to dual-boot, please reboot using the"
                          " legacy mode.\n"
                          "Otherwise, you may wipe disks in the next screen"))
        label.set_property("xalign", 0.5)
        label.set_use_markup(True)
        self.pack_start(label, False, False, 10)

        button = Gtk.Button.new_with_label("Continue")
        button.get_style_context().add_class("destructive-action")
        button.set_halign(Gtk.Align.CENTER)
        self.pack_start(button, False, False, 10)

        button.connect("clicked", self.on_clicked)

        self.set_valign(Gtk.Align.CENTER)
        self.set_halign(Gtk.Align.CENTER)

    def on_clicked(self, btn, w=None):
        """ Update owner page """
        self.owner.can_continue = True
        self.owner.info.owner.set_can_next(True)
        self.owner.stack.set_visible_child_name("chooser")


class ChooserPage(Gtk.VBox):
    """ Main chooser UI """

    combo = None
    strategy_box = None
    respond = False
    manager = None
    drives = None

    # To record the strategy.
    info = None

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
        drive = self.drives[combo.get_active_id()]
        strats = self.manager.get_strategies(drive)

        self.reset_options()
        leader = None
        for strat in strats:
            # update it
            strat.update_operations(self.info.owner.get_disk_manager(),
                                    self.info)
            button = Gtk.RadioButton.new_with_label_from_widget(
                leader, strat.get_display_string())
            button.strategy = strat
            if not leader:
                leader = button
            button.get_child().set_use_markup(True)
            button.connect("toggled", self.on_radio_toggle)
            self.strategy_box.pack_start(button, False, False, 8)
            button.show_all()
        # Force selection
        if leader:
            self.on_radio_toggle(leader)

    def reset_options(self):
        """ Reset available strategies """
        for widget in self.strategy_box.get_children():
            widget.destroy()

    def on_radio_toggle(self, radio, w=None):
        """ Handle setting of a strategy """
        if not radio.get_active():
            return
        strat = radio.strategy
        self.info.strategy = strat

    def reset(self):
        self.respond = False
        self.drives = dict()
        self.combo.remove_all()
        self.reset_options()
        self.respond = True

    def set_drives(self, info, prober):
        """ Set the display drives """
        self.info = info
        self.info.strategy = None
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

        label = Gtk.Label("<big>{}</big>".format(
                          "Oh no! Your system has no disks available.\n"
                          "There is nowhere to install Solus."))
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
    can_continue = False

    def __init__(self):
        BasePage.__init__(self)

        self.stack = Gtk.Stack()
        self.pack_start(self.stack, True, True, 0)

        self.spinner = LoadingPage()

        self.whoops = WhoopsPage()
        self.stack.add_named(self.whoops, "whoops")
        broken = BrokenWindowsPage(self)
        self.stack.add_named(broken, "broken-windows")
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
        self.info.prober = self.prober
        self.prober.probe()
        perms.down_permissions()

        # Currently the only GTK call here
        Gdk.threads_enter()
        self.info.owner.set_can_previous(True)
        can_continue = True

        if len(self.prober.drives) == 0:
            # No drives
            self.stack.set_visible_child_name("whoops")
            can_continue = False
        elif self.prober.is_broken_windows_uefi():
            self.stack.set_visible_child_name("broken-windows")
            self.can_continue = False
        else:
            # Let them choose
            self.stack.set_visible_child_name("chooser")
            self.can_continue = True
        self.spinner.stop()
        Gdk.threads_leave()

        if can_continue:
            GLib.idle_add(self.update_disks)

    def update_disks(self):
        """ Thread load finished, update UI from discovered info """
        self.chooser.set_drives(self.info, self.prober)
        self.info.windows_present = False
        for drive in self.prober.drives:
            for os in drive.operating_systems:
                os_ = drive.operating_systems[os]
                if os_.otype == "windows":
                    self.info.windows_present = True
                    break

        # Allow forward navigation now
        self.info.owner.set_can_next(self.can_continue)
        return False

    def init_view(self):
        """ Prepare for viewing... """
        if self.had_init:
            return
        self.had_init = True
        self.stack.set_visible_child_name("loading")
        self.spinner.start()
        self.spinner.show_all()
        GLib.idle_add(self.prepare_view)

    def prepare_view(self):
        """ Do the real job after GTK has done things.. """
        self.info.owner.set_can_previous(False)
        self.queue_draw()

        t = threading.Thread(target=self.load_disks)
        t.daemon = True
        t.start()
        return False

    def prepare(self, info):
        self.info = info
        self.init_view()
        self.info.owner.set_can_next(self.can_continue)
