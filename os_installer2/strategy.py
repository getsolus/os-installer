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

MB = 1000 * 1000
GB = 1000 * MB
MIN_REQUIRED_SIZE = 10 * GB
SWAP_USE_THRESHOLD = 15 * GB
ESP_FREE_REQUIRED = 60 * MB


def find_best_swap_size(longsize):
    gbs = longsize / GB
    if gbs > 50:
        return 4 * GB
    elif gbs > 40:
        return 2 * GB
    else:
        return 1 * GB


class DiskStrategy:
    """ Base DiskStrategy does nothing """

    priority = 0
    drive = None
    dp = None

    def __init__(self, dp, drive):
        self.drive = drive
        self.dp = dp
        self.get_suitable_esp()

    def get_display_string(self):
        return "Fatal Error"

    def get_name(self):
        return "-fatal-"

    def is_possible(self):
        return False

    def get_priority(self):
        return self.priority

    def explain(self, dm):
        """ Step by step explanation of what we're doing to do. """
        return []

    def is_uefi(self):
        """ proxy """
        return self.dp.dm.is_efi_booted()

    def get_suitable_esp(self):
        """ Attempt to find the suitable ESP.... """
        l = self.dp.collect_esp()
        if not l:
            return None
        e = l[0]
        if e.freespace < ESP_FREE_REQUIRED:
            return None
        return e

    def get_boot_loader_options(self):
        """ No boot loader options available. """
        return []


class EmptyDiskStrategy(DiskStrategy):
    """ There is an empty disk, use this if it is big enough """
    drive = None

    priority = 50

    def __init__(self, dp, drive):
        DiskStrategy.__init__(self, dp, drive)
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

    def explain(self, dm):
        ret = []
        ret.append("Use entire disk..")
        return ret


class WipeDiskStrategy(DiskStrategy):
    """ We simply wipe and take over a complete disk """
    drive = None

    priority = 20

    def __init__(self, dp, drive):
        DiskStrategy.__init__(self, dp, drive)
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

    def get_boot_loader_options(self):
        if not self.is_uefi():
            paths = [
                x.path for x in self.dp.drives if x.path != self.drive.path
            ]
            paths.append(self.drive.path)
            paths.reverse()
            return paths
        esps = self.dp.collect_esp()
        if len(esps) == 0:
            return ["Create new ESP on {}".format(self.drive.path)]
        cand = self.get_suitable_esp()
        # Are we overwriting this ESP?
        if esps[0].partition.disk == self.drive.disk:
            return ["Create new ESP on {}".format(self.drive.path)]
        if not cand:
            return ["ESP is too small: {} free space remaining".format(
                cand.freespace_string)]
        return [cand.path]


class UseFreeSpaceStrategy(DiskStrategy):
    """ Use free space on the device """
    drive = None

    potential_spots = None
    candidate = None

    priority = 30

    def __init__(self, dp, drive):
        DiskStrategy.__init__(self, dp, drive)
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

    # Selected OS name
    candidate_os = None

    # Selected OS
    sel_os = None
    priority = 40

    our_size = 0
    their_size = 0

    def __init__(self, dp, drive):
        DiskStrategy.__init__(self, dp, drive)
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

    def set_our_size(self, sz):
        self.our_size = sz

    def set_their_size(self, sz):
        self.their_size = sz

    def explain(self, dm):
        ret = []
        their_new = dm.format_size_local(self.their_size, True)
        their_old = dm.format_size_local(self.candidate_part.size, True)

        ret.append("Resize {} ({}) from {} to {}".format(
            self.candidate_os, self.candidate_part.path,
            their_old, their_new))

        tnew = self.our_size
        # Find swap
        swap = self.drive.get_swap_partitions()
        swap_part = None
        if swap:
            swap_part = swap[0]
        if swap_part:
            ret.append("Use {} as swap partition".format(swap_part.path))
        else:
            if tnew >= SWAP_USE_THRESHOLD:
                new_swap_size = find_best_swap_size(self.our_size)
                tnew -= new_swap_size
                new_sz = dm.format_size_local(new_swap_size, True)
                ret.append("Create {} swap partition".format(new_sz))

        our_new = dm.format_size_local(tnew, True)
        ret.append("Install Solus in remaining {}".format(our_new))

        return ret

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
                    continue
                log_parts = self.drive.disk.getLogicalPartitions()
                max_logical = self.drive.disk.getMaxLogicalPartitions()
                if len(log_parts) >= max_logical:
                    continue
            # Can continue
            self.potential_spots.append(partition)

        self.potential_spots.sort(key=SystemPartition.getLength,
                                  reverse=True)
        if len(self.potential_spots) > 0:
            self.candidate_part = self.potential_spots[0]
            self.sel_os = \
                self.drive.operating_systems[self.candidate_part.path]
            self.candidate_os = self.sel_os.name
            # Default to using the whole thing =P
            self.set_our_size(
                self.candidate_part.size - self.candidate_part.usedspace)
            self.set_their_size(self.candidate_part.size - MIN_REQUIRED_SIZE)
            return True
        return False


class UserPartitionStrategy(DiskStrategy):
    """ Just for consistency and ease in integration, let the user do the
        partitioning """
    drive = None

    priority = 10

    def __init__(self, dp, drive):
        DiskStrategy.__init__(self, dp, drive)
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
    broken_uefi = False

    def __init__(self, prober):
        self.prober = prober
        self.broken_uefi = prober.is_broken_windows_uefi()

    def get_strategies(self, drive):
        ret = []
        # Possible strategies
        strats = [
            WipeDiskStrategy,
            UserPartitionStrategy,
            EmptyDiskStrategy,
        ]
        # In short, you're in the wrong mode.
        if not self.broken_uefi:
            strats.extend([
                UseFreeSpaceStrategy,
                DualBootStrategy,
            ])
        for pot in strats:
            i = pot(self.prober, drive)
            if not i.is_possible():
                continue
            ret.append(i)
        ret.sort(key=DiskStrategy.get_priority, reverse=True)
        return ret
