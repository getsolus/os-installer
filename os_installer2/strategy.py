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

GiB = 1024 * 1024 * 1024
MIN_REQUIRED_SIZE = 30 * GiB


class DiskStrategy:
    """ Base DiskStrategy does nothing """

    def get_display_string(self):
        return "Fatal Error"

    def get_name(self):
        return "-fatal-"

    def is_possible(self):
        return False


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

    def is_possible(self):
        if self.drive.size < MIN_REQUIRED_SIZE:
            return False
        return True


class UseFreeSpaceStrategy(DiskStrategy):
    """ Use free space on the device """
    drive = None

    potential_spots = []
    candidate = None

    def __init__(self, drive):
        self.drive = drive

    def get_display_string(self):
        sz = "Use the remaining free space on this disk and install a fresh" \
             "copy of Solus\nThis will not affect other systems."
        return sz

    def get_name(self):
        return "use-free-space: {}".format(self.drive.path)

    def is_possible(self):
        # No disk, should be wipe-disk strategy
        if not self.drive.disk:
            return False
        # Build up a selection of free space partitions to use
        for part in self.drive.disk.getFreeSpacePartitions():
            size = part.getLength() * self.drive.device.sectorSize
            if size >= MIN_REQUIRED_SIZE:
                self.potential_spots.append(part)
        self.potential_spots.sort(key=parted.Partition.getLength, reverse=True)
        # Got at least one space big enough to use
        if len(self.potential_spots) > 0:
            # Pick the biggest guy
            self.candidate = self.potential_spots[0]
            return True
        return False


class DualBootStrategy(DiskStrategy):
    """ Dual-boot alongside the biggest install by resizing it """
    drive = None

    def __init__(self, drive):
        self.drive = drive

    def get_display_string(self):
        return "TODO: Add intelligent string"

    def get_name(self):
        return "dual-boot: {}".format(self.drive.path)

    def is_possible(self):
        return False


class UserPartitionStrategy(DiskStrategy):
    """ Just for consistency and ease in integration, let the user do the
        partitioning """
    drive = None

    def __init__(self, drive):
        self.drive = drive

    def get_display_string(self):
        # TODO: Make better
        return "Partition this drive yourself"

    def get_name(self):
        return "custom-partition: {}".format(self.drive.path)

    def is_possible(self):
        return self.drive.size >= MIN_REQUIRED_SIZE


class DiskStrategyManager:
    """ Strategy manager for installation solutions """

    prober = None

    def __init__(self, prober):
        self.prober = prober

    def get_strategies(self, drive):
        ret = []
        # Possible strategies
        strats = [
            WipeDiskStrategy,
            UseFreeSpaceStrategy,
            DualBootStrategy,
            UserPartitionStrategy
        ]

        for pot in strats:
            i = pot(drive)
            if not i.is_possible():
                continue
            ret.append(i)
        return ret
