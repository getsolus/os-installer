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

import re
import os


class DiskManager:
    """ Manage all disk operations """

    re_whole_disk = None
    re_mmcblk = None
    re_nvme = None
    re_raid = None
    devices = None

    def __init__(self):
        # Gratefully borrowed from gparted, Proc_Partitions_Info.cc
        self.re_whole_disk = re.compile(
            "^[\t ]+[0-9]+[\t ]+[0-9]+[\t ]+[0-9]+[\t ]+([^0-9]+)$")
        self.re_mmcblk = re.compile(
            "^[\t ]+[0-9]+[\t ]+[0-9]+[\t ]+[0-9]+[\t ]+(mmcblk[0-9]+)$")
        self.re_nvme = re.compile(
            "^[\t ]+[0-9]+[\t ]+[0-9]+[\t ]+[0-9]+[\t ]+(nvme[0-9]+n[0-9]+)$")
        self.re_raid = re.compile(
            "^[\t ]+[0-9]+[\t ]+[0-9]+[\t ]+[0-9]+[\t ]+(md[0-9]+)$")
        self.scan_parts()

    def scan_parts(self):
        self.devices = []
        try:
            part_file = open("/proc/partitions")
        except Exception as ex:
            print("Failed to scan parts: %s" % ex)
            return

        for line in part_file.readlines():
            device = None

            # readlines doesn't consume
            line = line.replace("\r", "").replace("\n", "")

            m = self.re_whole_disk.match(line)
            if m:
                device = m.group(1)
                self.push_device(device)
                continue

            m = self.re_mmcblk.match(line)
            if m:
                device = m.group(1)
                self.push_device(device)
                continue

            m = self.re_nvme.match(line)
            if m:
                device = m.group(1)
                self.push_device(device)
                continue

            m = self.re_raid.match(line)
            if m:
                device = m.group(1)
                self.push_device(device)

        part_file.close()

    def push_device(self, device):
        """ Push a newly discovered device into the list """
        fpath = "/dev/{}".format(str(device))
        if not os.path.exists(fpath):
            print("Debug: Non-existent node: %s" % fpath)
            return

        if device not in self.devices:
            print("Debug: Discovered %s" % fpath)
            self.devices.append(fpath)
