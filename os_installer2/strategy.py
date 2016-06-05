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

import parted


class DiskStrategy:
    """ Base DiskStrategy does nothing """

    def get_display_string(self):
        return "Fatal Error"

    def get_name(self):
        return "-fatal-"


class WipeDiskStrategy(DiskStrategy):
    """ We simply wipe and take over a complete disk """
    drive = None

    def __init__(self, drive):
        self.drive = drive

    def get_display_string(self):
        sz = "Erase all content on this disk and install a fresh copy of " \
             "Solus\nThis will <b>destroy all existing data on the disk</b>."
        return sz

    def get_name(self):
        return "wipe-disk: {}".format(self.drive.path)


class DiskStrategyManager:
    """ Strategy manager for installation solutions """

    prober = None
    min_required_size = 0

    def __init__(self, prober):
        self.prober = prober
        GiB = 1024 * 1024 * 1024
        self.min_required_size = 30 * GiB

    def get_strategies(self, drive):
        ret = []
        # Not big enough for any strategy
        if drive.size < self.min_required_size:
            return ret

        ret.append(WipeDiskStrategy(drive))
        return ret
