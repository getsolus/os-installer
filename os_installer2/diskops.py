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

from os_installer2 import format_size_local


class BaseDiskOp:
    """ Basis of all disk operations """

    device = None

    def __init__(self, device):
        self.device = device
        pass

    def describe(self):
        """ Describe this operation """
        return None

    def apply(self, disk):
        """ Apply this operation on the given (optional) disk"""
        return False


class DiskOpCreateDisk(BaseDiskOp):
    """ Create a new parted.Disk """

    disk = None
    label = None

    def __init__(self, device, label):
        BaseDiskOp.__init__(self, device)
        self.label = label

    def describe(self):
        return "Create {} partition table on {}".format(
            self.label, self.device.path)


class DiskOpCreatePartition(BaseDiskOp):
    """ Create a new partition on the disk """

    fstype = None
    size = None
    ptype = None

    def __init__(self, device, ptype, fstype, size):
        BaseDiskOp.__init__(self, device)
        self.ptype = ptype
        self.fstype = fstype
        self.size = size

    def describe(self):
        return "I should be described by my children. ._."


class DiskOpCreateSwap(DiskOpCreatePartition):
    """ Create a new swap partition """

    def __init__(self, device, ptype, size):
        DiskOpCreatePartition.__init__(
            self,
            device,
            ptype,
            "linux-swap(v1)",
            size)

    def describe(self):
        return "Create {} swap partition on {}".format(
            format_size_local(self.size, True), self.device.path)


class DiskOpCreateESP(DiskOpCreatePartition):
    """ Create a new ESP """

    def __init__(self, device, ptype, size):
        DiskOpCreatePartition.__init__(
            self,
            device,
            ptype,
            "fat32",
            size)

    def describe(self):
        return "Create {} EFI System Partition on {}".format(
            format_size_local(self.size, True), self.device.path)


class DiskOpCreateRoot(DiskOpCreatePartition):
    """ Create a new root partition """

    def __init__(self, device, ptype, size):
        DiskOpCreatePartition.__init__(
            self,
            device,
            ptype,
            "ext4",
            size)

    def describe(self):
        return "Create {} root partition on {}".format(
            format_size_local(self.size, True), self.device.path)


class DiskOpUseSwap(BaseDiskOp):
    """ Use an existing swap paritition """

    swap_part = None

    def __init__(self, device, swap_part):
        BaseDiskOp.__init__(self, device)
        self.swap_part = swap_part

    def describe(self):
        return "Use {} as swap partition".format(self.swap_part.path)


class DiskOpResizeOS(BaseDiskOp):
    """ Resize an operating system """

    their_size = None
    our_size = None
    desc = None

    def __init__(self, device, part, os, their_size, our_size):
        BaseDiskOp.__init__(self, device)

        self.their_size = their_size
        self.our_size = our_size

        their_new_sz = format_size_local(their_size, True)
        their_old_sz = format_size_local(part.size, True)

        self.desc = "Resize {} ({}) from {} to {}".format(
            os, part.path, their_old_sz, their_new_sz)

    def describe(self):
        return self.desc


class DiskOpFormatPartition(BaseDiskOp):
    """ Format one thing as another """

    format_type = None
    part = None

    def __init__(self, device, part, format_type):
        BaseDiskOp.__init__(self, device)
        self.part = part
        self.format_type = format_type

    def describe(self):
        return "Format {} as {}".format(self.part, self.format_type)


class DiskOpFormatRoot(DiskOpFormatPartition):
    """ Format the root partition """

    def __init__(self, device, part):
        DiskOpFormatPartition.__init__(self, device, part, "ext4")

    def describe(self):
        return "Use {} as {} root partition".format(
            self.part, self.format_type)
