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
from .diskman import SystemPartition

GiB = 1024 * 1024 * 1024
MIN_REQUIRED_SIZE = 10 * GiB


class DiskStrategy:
    """ Base DiskStrategy does nothing """

    priority = 0

    def get_display_string(self):
        return "Fatal Error"

    def get_name(self):
        return "-fatal-"

    def is_possible(self):
        return False

    def get_priority(self):
        return self.priority


class EmptyDiskStrategy(DiskStrategy):
    """ There is an empty disk, use this if it is big enough """
    drive = None

    priority = 50

    def __init__(self, drive):
        self.drive = drive

    def get_display_string(self):
        sz = "Automatically partition this empty disk and install a fresh " \
             "copy of Solus."
        return sz

    def get_name(self):
        return "empty-disk: {}".format(self.drive.path)

    def is_possible(self):
        if self.drive.size < MIN_REQUIRED_SIZE:
            return False
        # No MBR/header
        if not self.drive.disk:
            return True
        if len(self.drive.disk.partitions) == 0:
            return True
        # Probably wipe-disk
        return False


class WipeDiskStrategy(DiskStrategy):
    """ We simply wipe and take over a complete disk """
    drive = None

    priority = 20

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
        # No table, use empty-disk strategy
        if not self.drive.disk:
            return False
        # This is an empty-disk strategy
        if len(self.drive.disk.partitions) == 0:
            return False
        return True


class UseFreeSpaceStrategy(DiskStrategy):
    """ Use free space on the device """
    drive = None

    potential_spots = None
    candidate = None

    priority = 30

    def __init__(self, drive):
        self.drive = drive
        self.potential_spots = []

    def get_display_string(self):
        sz = "Use the remaining free space on this disk and install a fresh" \
             " copy of Solus\nThis will <b>not affect</b> other systems."
        return sz

    def get_name(self):
        return "use-free-space: {}".format(self.drive.path)

    def is_possible(self):
        # No disk, should be empty-disk strategy
        if not self.drive.disk:
            return False
        # No partitions at all, empty-disk
        if len(self.drive.disk.partitions) == 0:
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
    potential_spots = None
    candidate_part = None
    candidate_os = None

    priority = 40

    def __init__(self, drive):
        self.drive = drive
        self.potential_spots = []

    def get_display_string(self):
        os = self.candidate_os
        sz = "Install a fresh copy of Solus alongside your existing " \
             "Operating System.\nYou can choose how much space Solus should " \
             "use in the next screen.\nThis will resize <b>%s</b>." % os
        return sz

    def get_name(self):
        return "dual-boot: {}".format(self.candidate_os)

    def is_possible(self):
        # Require table
        if not self.drive.disk:
            return False
        for os_part in self.drive.operating_systems:
            if os_part not in self.drive.partitions:
                print("Warning: missing os_part: {}".format(os_part))
                continue
            partition = self.drive.partitions[os_part]
            if partition.size < MIN_REQUIRED_SIZE:
                continue
            if partition.freespace < MIN_REQUIRED_SIZE:
                continue
            # Now figure out if there is somewhere to put ourselves..
            primaries = self.drive.disk.getPrimaryPartitions()
            ext = self.drive.disk.getExtendedPartition()
            max_prim = self.drive.disk.maxPrimaryPartitionCount
            if ext:
                max_prim -= 1
            if len(primaries) == max_prim:
                if not ext:
                    print("Debug: Max partitions hit on {} (no extended)".
                          format(self.drive.path))
                    continue
                log_parts = self.drive.disk.getLogicalPartitions()
                max_logical = self.drive.disk.getMaxLogicalPartitions()
                if len(log_parts) >= max_logical:
                    print("Logical primary partition count exceeded on {}".
                          format(self.drive.path))
                    continue
                print("%s logicals now left" % (max_logical - len(log_parts)))
            else:
                print("Debug: {} remaining primaries on {}".
                      format(max_prim - len(primaries), self.drive.path))
            # Can continue
            self.potential_spots.append(partition)

        self.potential_spots.sort(key=SystemPartition.getLength,
                                  reverse=True)
        if len(self.potential_spots) > 0:
            self.candidate_part = self.potential_spots[0]
            self.candidate_os = \
                self.drive.operating_systems[self.candidate_part.path].name
            return True
        return False


class UserPartitionStrategy(DiskStrategy):
    """ Just for consistency and ease in integration, let the user do the
        partitioning """
    drive = None

    priority = 10

    def __init__(self, drive):
        self.drive = drive

    def get_display_string(self):
        sz = "Create, resize and manually configure disk partitions yourself" \
             ". This method\nmay lead to <b>data loss.</b>"
        return sz

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
            UserPartitionStrategy,
            EmptyDiskStrategy
        ]
        for pot in strats:
            i = pot(drive)
            if not i.is_possible():
                continue
            ret.append(i)
        ret.sort(key=DiskStrategy.get_priority, reverse=True)
        return ret
