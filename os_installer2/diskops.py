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


class DiskOpCreateDisk:
    """ Create a new parted.Disk """

    disk = None
    label = None

    def __init__(self, device, label):
        BaseDiskOp.__init__(self, device)
        self.label = label

    def describe(self):
        return "Create {} partition table on {}".format(
            self.label, self.device.path)


class DiskOpCreatePartition:
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


class DiskOpUseSwap:
    """ Use an existing swap paritition """

    swap_part = None

    def __init__(self, device, swap_part):
        BaseDiskOp.__init__(self, device)
        self.swap_part = swap_part

    def describe(self):
        return "Use {} as swap partition".format(self.swap_part.path)
