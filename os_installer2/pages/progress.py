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
from collections import OrderedDict
from os_installer2 import SOURCE_FILESYSTEM, INNER_FILESYSTEM
import os


# Update 5 times a second, vs every byte copied..
UPDATE_FREQUENCY = 1000 / 5


class InstallerProgressPage(BasePage):
    """ Actual installation :o """

    info = None
    progressbar = None
    label = None
    had_start = False
    installing = False
    mount_tracker = None
    temp_dirs = None

    # Our disk manager
    dm = None

    # Current string for the idle monitor to display in Gtk thread
    display_string = None

    # How much we need to copy
    filesystem_source_size = 0

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

        self.mount_tracker = OrderedDict()
        self.temp_dirs = []

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
        print(sz)

    def idle_monitor(self):
        """ Called periodicially so we can update our view """
        self.label.set_markup(self.get_display_string())
        self.progressbar.pulse()
        if not self.installing:
            print("Finished idle_monitor")
        return self.installing

    def prepare(self, info):
        self.info = info
        self.dm = info.owner.get_disk_manager()
        self.info.owner.set_can_next(False)
        self.info.owner.set_can_previous(False)
        self.info.owner.set_can_quit(False)

        if not self.had_start:
            self.had_start = True
            self.begin_install()

    def _mkdtemp(self, suffix='installer'):
        """ Create and track the temporary directory """
        d = self.dm.create_temp_dir()
        if not d:
            return None
        self.temp_dirs.append(d)
        return d

    def get_mount_point_for(self, node):
        """ Get the mount point of a given node """
        if node in self.mount_tracker:
            return self.mount_tracker[node]
        return None

    def mount_source_filesystem(self):
        """ Mount the source and child """
        source = self._mkdtemp()
        inner_path = os.path.join(source, INNER_FILESYSTEM)
        if not source:
            self.set_display_string("Cannot mkdtemp")
            return False

        # Try to mount the squashfs
        if not self.dm.do_mount(SOURCE_FILESYSTEM, source, "auto", "loop"):
            self.set_display_string("Cannot mount source filesystem")
            return False
        self.mount_tracker[SOURCE_FILESYSTEM] = source

        # See if the kid exists or not
        if not os.path.exists(inner_path):
            self.set_display_string("Cannot find {}".format(inner_path))
            return False

        inner_child = self._mkdtemp()
        # Try to mount the kid to a new temp
        if not inner_child:
            self.set_display_string("Cannot mkdtemp")
            return False
        if not self.dm.do_mount(inner_path, inner_child, "auto", "loop"):
            self.set_display_string("Cannot mount inner child")
            return False
        self.mount_tracker[INNER_FILESYSTEM] = inner_child

        # Now grab the size of the source filesystem
        try:
            vfs = os.statvfs(inner_child)
            size = (vfs.f_blocks - vfs.f_bfree) * vfs.f_frsize
            self.filesystem_source_size = size
        except Exception as e:
            self.set_display_string("Cannot compute source size: {}".format(e))
            return False

        return True

    def unmount_all(self):
        """ umount everything we've mounted """
        ret = True

        # Visit in reverse order
        keys = self.mount_tracker.keys()
        keys.reverse()
        for key in keys:
            if not self.dm.do_umount(self.mount_tracker[key]):
                self.set_display_string("Cannot umount {}".format(key))
                ret = False

        for tmp in self.temp_dirs:
            try:
                os.rmdir(tmp)
            except Exception as e:
                self.set_display_string("Cannot rmdir {}: {}".format(
                    tmp, e))
                ret = False
        return ret

    def copy_system(self):
        """ Attempt to copy the entire filesystem across """
        print("Need to copy {} bytes".format(self.filesystem_source_size))

        source_fs = self.get_mount_point_for(INNER_FILESYSTEM)
        if not source_fs:
            return False

        # Ensure we don't follow links, i.e. we're never in a situation where
        # we're creating broken leading directories
        count = 0
        for root, dirs, files in os.walk(source_fs,
                                         topdown=False,
                                         followlinks=False):
            # Walk the tree from the back to restore permissions properly
            count += len(files)
            pass
        print("DEBUG: Counted {} files".format(count))
        return False

    def install_thread(self):
        """ Handle the real work of installing =) """
        self.set_display_string("Analyzing installation configuration")

        # immediately gain privs
        self.info.owner.get_perms_manager().up_permissions()

        # TODO: Apply disk strategies!!
        strategy = self.info.strategy
        for op in strategy.get_operations():
            self.set_display_string(op.describe())
            time.sleep(1)

        # Now mount up as it were.
        if not self.mount_source_filesystem():
            self.unmount_all()
            self.set_display_string("Failed to mount!")
            self.installing = False
            return

        # TODO: Mount target filesystem

        # Copy source -> target
        if not self.copy_system():
            self.unmount_all()
            self.set_display_string("Failed to copy filesystem")
            self.installing = False
            return

        time.sleep(1)
        self.set_display_string("Nah only kidding")

        # Ensure the idle monitor stops
        if not self.unmount_all():
            self.set_display_string("Failed to unmount cleanly!")

        self.installing = False
