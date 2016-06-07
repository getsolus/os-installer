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
import parted


class BaseDiskOp:
    """ Basis of all disk operations """

    device = None
    errors = None
    part_offset = 0

    def __init__(self, device):
        self.device = device
        pass

    def describe(self):
        """ Describe this operation """
        return None

    def apply(self, disk):
        """ Apply this operation on the given (optional) disk"""
        print("IMPLEMENT ME!")
        return False

    def get_errors(self):
        """ Get the errors, if any, encountered """
        return self.errors

    def set_errors(self, er):
        """ Set the errors encountered """
        self.errors = er

    def set_part_offset(self, newoffset):
        """ Useful only for new partitions """
        self.part_offset = newoffset


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

    def apply(self, unused_disk):
        """ Construct a new labeled disk """
        try:
            d = parted.freshDisk(self.device, self.label)
            self.disk = d
        except Exception as e:
            self.set_errors(e)
            return False
        return True


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
        if not self.ptype:
            self.ptype = parted.PARTITION_NORMAL

    def describe(self):
        return "I should be described by my children. ._."

    def apply(self, disk):
        """ Create a partition with the given type... """
        try:
            length = parted.sizeToSectors(
                self.size, 'B', disk.device.sectorSize)
            geom = parted.Geometry(
                device=self.device, start=self.part_offset, length=length)
            fs = parted.FileSystem(type=self.fstype, geometry=geom)
            p = parted.Partition(
                disk=disk, type=self.ptype, fs=fs, geometry=geom)

            disk.addPartition(
                p, constraint=self.device.optimalAlignedConstraint)
        except Exception as e:
            self.set_errors(e)
            return False
        return True


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
    part = None

    def __init__(self, device, part, os, their_size, our_size):
        BaseDiskOp.__init__(self, device)

        self.their_size = their_size
        self.our_size = our_size
        self.part = part.partition

        their_new_sz = format_size_local(their_size, True)
        their_old_sz = format_size_local(part.size, True)

        self.desc = "Resize {} ({}) from {} to {}".format(
            os, part.path, their_old_sz, their_new_sz)

    def describe(self):
        return self.desc

    def apply(self, disk):
        # TODO: Actually resize the filesystem itself
        try:
            self.part.geometry.length = self.their_size
            return True
        except Exception, e:
            self.set_errors(e)
            return False


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
