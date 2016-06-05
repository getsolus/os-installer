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
from gi.repository import Gtk
import sys


class DualBootPage(Gtk.VBox):
    """ Used to manage the dual boot configuration settings,
        essentially we're just here to resize the users partititon
        and make room for Solus. """

    def __init__(self):
        Gtk.VBox.__init__(self)

    def update_strategy(self, info):
        info.owner.set_can_next(True)


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
