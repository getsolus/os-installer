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
from os_installer2.strategy import DualBootStrategy
from os_installer2.strategy import EmptyDiskStrategy
from os_installer2.strategy import WipeDiskStrategy
from os_installer2.strategy import UseFreeSpaceStrategy
from os_installer2.strategy import UserPartitionStrategy
from os_installer2.strategy import MIN_REQUIRED_SIZE
from gi.repository import Gtk
import sys


class DualBootPage(Gtk.VBox):
    """ Used to manage the dual boot configuration settings,
        essentially we're just here to resize the users partititon
        and make room for Solus. """

    image = None
    label = None
    spin = None
    info_label = None
    size_label = None
    info = None

    def __init__(self):
        Gtk.VBox.__init__(self)

        self.set_border_width(40)

        self.info_label = Gtk.Label.new("")
        self.pack_start(self.info_label, False, False, 0)
        self.info_label.set_margin_bottom(10)
        self.info_label.set_halign(Gtk.Align.START)

        # Construct dual-boot row
        hbox = Gtk.HBox(0)
        hbox.set_margin_top(20)
        self.pack_start(hbox, False, False, 0)

        self.image = Gtk.Image.new()
        self.image.set_margin_end(12)
        hbox.pack_start(self.image, False, False, 0)

        self.label = Gtk.Label.new("")
        self.label.set_margin_end(20)
        self.label.set_halign(Gtk.Align.START)
        hbox.pack_start(self.label, False, False, 0)

        self.spin = Gtk.SpinButton.new_with_range(0, 1000, 10)
        self.spin.connect("value-changed", self.on_value_changed)
        hbox.pack_start(self.spin, False, False, 5)
        lab = Gtk.Label.new("GB")
        hbox.pack_start(lab, False, False, 1)
        lab.set_halign(Gtk.Align.START)

        lab2 = Gtk.Label.new("New size for your existing installation")
        lab2.set_margin_start(20)
        hbox.pack_start(lab2, False, False, 4)
        lab2.get_style_context().add_class("dim-label")

        # Now start our row
        hbox = Gtk.HBox(0)
        hbox.set_margin_top(20)
        self.pack_start(hbox, False, False, 0)

        # our icon
        sz = Gtk.IconSize.DIALOG
        image = Gtk.Image.new_from_icon_name("distributor-logo-solus", sz)
        image.set_pixel_size(64)
        image.set_margin_end(12)
        hbox.pack_start(image, False, False, 0)

        # our label
        label = Gtk.Label.new("<big>New Solus Installation</big>")
        label.set_use_markup(True)
        label.set_margin_end(20)
        label.set_halign(Gtk.Align.START)
        hbox.pack_start(label, False, False, 0)

        self.size_label = Gtk.Label.new("0GB")
        self.size_label.set_margin_start(20)
        hbox.pack_start(self.size_label, False, False, 4)

    def on_value_changed(self, spin, w=None):
        if not self.info:
            return

        val = self.spin.get_value()
        avail = self.info.strategy.candidate_part.size
        GB = 1000.0 * 1000.0 * 1000.0

        nval = (avail / GB) - val
        dm = self.info.owner.get_disk_manager()
        ssize = dm.format_size_local(nval * GB, double_precision=True)
        self.size_label.set_markup(ssize)

    def update_strategy(self, info):
        self.info = info
        info.owner.set_can_next(True)
        os = info.strategy.sel_os
        self.image.set_from_icon_name(os.icon_name, Gtk.IconSize.DIALOG)
        self.image.set_pixel_size(64)
        self.label.set_markup("<big>%s</big>" % os.name)

        dm = info.owner.get_disk_manager()

        used = info.strategy.candidate_part.usedspace
        avail = info.strategy.candidate_part.size

        GB = 1000.0 * 1000.0 * 1000.0
        min_gb = MIN_REQUIRED_SIZE
        dmin = float(used / GB)
        dmax = float((avail - min_gb) / GB)
        # Set upper minimum size for the new Solus

        adju = Gtk.Adjustment.new(dmin, dmin, dmax, 1, 10, 0)
        self.spin.set_adjustment(adju)
        self.spin.set_digits(2)

        os_name = os.name
        # We need this much
        min_we_needs = dm.format_size_local(min_gb, double_precision=True)
        # They need this much
        min_they_needs = dm.format_size_local(used, double_precision=True)
        # Total of this much
        max_avail = dm.format_size_local(avail - used, double_precision=True)
        total_size = dm.format_size_local(avail, double_precision=True)

        l = "Resize the partition containing {} to make room for the " \
            "new Solus installation.\n" \
            "Solus requires a minimum of {} disk space for the installation" \
            ", so free up <b>at least {}</b>\nfrom the maximum available " \
            "{}\n{} will require a minimum of {} from the total {}".format(
                os_name, min_we_needs, min_we_needs, max_avail,
                "Your currently installed operating system", min_they_needs,
                total_size)
        self.info_label.set_markup(l)


class ManualPage(Gtk.VBox):
    """ Manual partitioning page, mostly TreeView with gparted proxy """

    def __init__(self):
        Gtk.VBox.__init__(self)

    def update_strategy(self, info):
        info.owner.set_can_next(False)


class InstallerPartitioningPage(BasePage):
    """ Dual boot + partitioning page """

    info = None
    stack = None

    # Dual boot page
    dbpage = None
    mpage = None

    def __init__(self):
        BasePage.__init__(self)
        self.stack = Gtk.Stack()
        # Reduce lag
        self.stack.set_transition_type(Gtk.StackTransitionType.NONE)
        self.pack_start(self.stack, True, True, 0)

        # Slow computers might show this page.. blank it
        label = Gtk.Label.new("")
        label.set_valign(Gtk.Align.CENTER)
        label.set_halign(Gtk.Align.CENTER)
        self.stack.add_named(label, "automatic")

        self.dbpage = DualBootPage()
        self.stack.add_named(self.dbpage, "dual-boot")

        self.mpage = ManualPage()
        self.stack.add_named(self.mpage, "manual")

        self.stack.set_visible_child_name("automatic")

    def get_title(self):
        return "Configure disks"

    def get_name(self):
        return "partitioning"

    def get_icon_name(self):
        return "drive-multidisk-symbolic"

    def prepare(self, info):
        self.info = info

        # Serious sanity stuffs
        if not info.strategy:
            print("FATAL: No strategy")
            sys.exit(0)

        skips = [
            EmptyDiskStrategy,
            WipeDiskStrategy,
            UseFreeSpaceStrategy,
        ]
        for sk in skips:
            if isinstance(info.strategy, sk):
                self.stack.set_visible_child_name("automatic")
                self.info.owner.skip_page()
                return
        if isinstance(info.strategy, DualBootStrategy):
            self.stack.set_visible_child_name("dual-boot")
            self.dbpage.update_strategy(info)
        elif isinstance(info.strategy, UserPartitionStrategy):
            self.mpage.update_strategy(info)
            self.stack.set_visible_child_name("manual")
        else:
            print("FATAL: Unknown strategy type!")
            sys.exit(0)
