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
import subprocess
import tempfile
import time


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
        print(self.get_mount_points())

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
        fpath = os.path.realpath(fpath)

        if device not in self.devices:
            ssd = str(self.is_device_ssd(fpath))
            print("Debug: Discovered %s (SSD? %s)" % (fpath, ssd))
            self.devices.append(fpath)

    def is_device_ssd(self, path):
        """ Determine if the device is an SSD """
        nodename = os.path.basename(path)
        fpath = "/sys/block/{}/queue/rotational".format(nodename)
        if not os.path.exists(fpath):
            return False

        # Don't try using SSD trim with eMMC
        if nodename.startswith("mmcblk"):
            return False

        try:
            with open(fpath, "r") as inp_file:
                items = inp_file.readlines()
                if len(items) == 1:
                    line = items[0].replace("\n", "").replace("\r", "")
                    if line == "0":
                        return True
        except Exception:
            pass
        return False

    def is_install_supported(self, path):
        """ Currently we only support rootfs installs on certain types... """
        nodename = os.path.basename(path)
        if nodename.startswith("md"):
            return False
        return True

    def get_mount_points(self):
        """ Return a mapping of device to mountpoint """
        ret = dict()

        with open("/proc/self/mounts", "r") as mpoints:
            for line in mpoints.readlines():
                line = line.replace("\n", "").replace("\r", "").strip()

                if line == "":
                    continue
                splits = line.split()
                if len(splits) < 4:
                    continue
                dev = splits[0]
                mpoint = splits[1]

                # Only interested in block devices
                if dev[0] != '/':
                    continue

                ret[os.path.abspath(os.path.realpath(dev))] = mpoint
        return ret

    def do_mount(self, device, mpoint, fsystem, options=None):
        """ Try to mount the device at mount_point """
        mount_cmd = "mount -t {} {} \"{}\"".format(device, mpoint, fsystem)

        if options:
            mount_cmd += "-o {}".format(options)

        try:
            subprocess.check_call(mount_cmd, shell=True)
        except Exception as e:
            print("Failed to mount %s to %s: %s" % (device, mpoint, e))
            return False
        return True

    def do_umount(self, thing):
        """ umount the given mountpoint/device """
        umount_cmd = "umount \"{}\"".format(thing)
        try_count = 0

        while (try_count < 3):
            try_count += 1
            try:
                subprocess.check_call(umount_cmd)
                return True
            except Exception:
                # wait 500ms, try again
                time.sleep(500)
                continue

        umount_cmd = "umount -l \"{}\"".format(thing)
        try:
            subprocess.check_call(umount_cmd)
            return True
        except Exception as e:
            print("Failed to unmount %s: %s" % (thing, e))
            return False

        # Finally umounted with lazy.
        return True

    def detect_operating_system(self, device, mpoints):
        """ Determine the operating system for a given device """
        mounted = False
        mount_point = None

        # Mount it if not already mounted
        if device not in mpoints:
            try:
                mount_point = tempfile.mkdtemp(suffix='installer')
            except Exception as e:
                print("Error creating mount point: %s" % e)
                return None
            if not self.do_mount(device, mount_point, "auto"):
                return None
            mounted = True
        else:
            # Reuse existing mountpoint
            mount_point = mpoints[device]

        # Do something interesting here
        print("Testing?!")

        # Unmount again
        if mounted:
            if self.do_umount(mount_point):
                try:
                    os.rmdir(mount_point)
                except Exception as e:
                    print("Failed to remove stagnant directory: %s" % e)
        return None
