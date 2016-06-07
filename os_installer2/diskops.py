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
import subprocess


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

    def apply(self, disk, simulate):
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

    def apply(self, unused_disk, simulate):
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
    part = None

    def __init__(self, device, ptype, fstype, size):
        BaseDiskOp.__init__(self, device)
        self.ptype = ptype
        self.fstype = fstype
        self.size = size
        if not self.ptype:
            self.ptype = parted.PARTITION_NORMAL

    def get_all_remaining_geom(self, device, start):
        length = device.getLength() - start
        length -= parted.sizeToSectors(1, 'MB', self.device.sectorSize)
        return parted.Geometry(device=device, start=start, length=length)

    def describe(self):
        return "I should be described by my children. ._."

    def apply(self, disk, simulate):
        """ Create a partition with the given type... """
        try:
            if not disk:
                raise RuntimeError("Cannot create partition on empty disk!")
            length = parted.sizeToSectors(
                self.size, 'B', disk.device.sectorSize)
            geom = parted.Geometry(
                device=self.device, start=self.part_offset, length=length)

            # Don't run off the end of the disk ...
            geom_cmp = self.get_all_remaining_geom(
                disk.device, self.part_offset)
            if geom_cmp.length < geom.length:
                print("Using new size of {} vs {}".format(
                    geom_cmp.length, geom.length))
                geom = geom_cmp

            fs = parted.FileSystem(type=self.fstype, geometry=geom)
            p = parted.Partition(
                disk=disk, type=self.ptype, fs=fs, geometry=geom)

            disk.addPartition(
                p, constraint=self.device.optimalAlignedConstraint)
            self.part = p
        except Exception as e:
            self.set_errors(e)
            return False
        return True

    def apply_format(self, disk):
        """ Post-creation all disks must be formatted """
        return False


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

    def apply_format(self, disk):
        cmd = "mkswap {}".format(self.part.path)
        try:
            subprocess.check_call(cmd, shell=True)
        except Exception as e:
            self.set_errors("{}: {}".format(self.part.path, e))
            return False
        return True


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

    def apply(self, disk, simulate):
        """ Create the fat partition first """
        b = DiskOpCreatePartition.apply(self, disk, simulate)
        if not b:
            return b
        try:
            self.part.setFlag(parted.PARTITION_BOOT)
        except Exception as e:
            self.set_errors("Cannot set ESP type: {}".format(e))
            return False
        return True

    def apply_format(self, disk):
        cmd = "mkdosfs -F 32 {}".format(self.part.path)
        try:
            subprocess.check_call(cmd, shell=True)
        except Exception as e:
            self.set_errors("{}: {}".format(self.part.path, e))
            return False
        return True


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

    def apply_format(self, disk):
        cmd = "mkfs.ext4 -F {}".format(self.part.path)
        try:
            subprocess.check_call(cmd, shell=True)
        except Exception as e:
            self.set_errors("{}: {}".format(self.part.path, e))
            return False
        return True


class DiskOpUseSwap(BaseDiskOp):
    """ Use an existing swap paritition """

    swap_part = None
    path = None

    def __init__(self, device, swap_part):
        BaseDiskOp.__init__(self, device)
        self.swap_part = swap_part
        self.path = self.swap_part.path

    def describe(self):
        return "Use {} as swap partition".format(self.swap_part.path)

    def apply(self, disk, simulate):
        """ Can't actually fail here. """
        return True


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

    def apply(self, disk, simulate):
        try:
            self.part.geometry.length = self.their_size
            cmd = None
            if self.part.fileSystem.type == "ntfs":
                cmd = "ntfsresize --size {} {}".format(
                    self.their_size, self.part.path)
                if simulate:
                    cmd += " --no-action"
                try:
                    subprocess.check_call(cmd, shell=True)
                except Exception as e:
                    self.set_errors(e)
                    return False
                return True
            elif self.part.fileSystem.type.startswith("ext"):
                if simulate:
                    return True
                cmd = "resize2fs {} {}".format(
                    self.part.path, self.their_size)
                try:
                    subprocess.check_call(cmd, shell=True)
                except Exception as ex:
                    self.set_errors(ex)
                    return False
            else:
                return False
        except Exception as e:
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
