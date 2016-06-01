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
import locale
import struct


class DiskManager:
    """ Manage all disk operations """

    re_whole_disk = None
    re_mmcblk = None
    re_nvme = None
    re_raid = None
    devices = None

    win_prefixes = None
    win_bootloaders = None

    is_uefi = False
    uefi_fw_size = 64
    host_size = 64

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

        # Rough versioning matches for Windows
        self.win_prefixes = {
            "10.": "Windows 10",
            "6.3": "Windows 8.1",
            "6.2": "Windows 8",
            "6.1": "Windows 7",
            "6.0": "Windows Vista",
            "5.2": "Windows XP",
            "5.1": "Windows XP",
            "5.0": "Windows 2000",
            "4.90": "Windows Me",
            "4.1": "Windows 98",
            "4.0.1381": "Windows NT",
            "4.0.950": "Windows 95",
        }

        # Rough match for BCD
        self.win_bootloaders = {
            "V.i.s.t.a": "Windows Vista bootloader",
            "W.i.n.d.o.w.s. .7": "Windows 7 bootloader",
            "W.i.n.d.o.w.s. .R.e.c.o.v.e.r.y. .E.n.v.i.r.o.n.m.e.n.t":
                "Windows recovery",
            "W.i.n.d.o.w.s. .S.e.r.v.e.r. .2.0.0.8":
                "Windows Server 2008 bootloader"
        }

        # Set up UEFI knowledge
        if os.path.exists("/sys/firmware/efi"):
            self.is_uefi = True
            pl_f = "/sys/firmware/efi/fw_platform_size"
            if os.path.exists(pl_f):
                pl_s = self._read_line_complete(pl_f)
                if pl_s == "64":
                    self.uefi_fw_size = 64
                elif pl_s == "32":
                    self.uefi_fw_size = 32
                else:
                    print("System reported odd FW size: {}".format(pl_s))
        else:
            self.is_uefi = False

        # host size setup (64/32)
        if struct.calcsize("P") * 8 < 64:
            self.host_size = 32
        else:
            self.host_size = 64

    def scan_parts(self):
        self.devices = []
        try:
            part_file = open("/proc/partitions")
        except Exception as ex:
            print("Failed to scan parts: %s" % ex)
            return

        groups = [self.re_whole_disk,
                  self.re_mmcblk,
                  self.re_nvme,
                  self.re_raid]

        for line in part_file.readlines():
            # readlines doesn't consume
            line = line.replace("\r", "").replace("\n", "")

            for x in groups:
                m = x.match(line)
                if not m:
                    continue
                self.push_device(m.group(1))
                break

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
            mount_cmd += " -o {}".format(options)

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

    def get_windows_version(self, path):
        """ Attempt to gain the Windows version """
        fpath = os.path.join(path, "Windows/servicing/Version")
        if not os.path.exists(fpath):
            # Still Windows of some variety
            fpath = os.path.join(path, "Windows/System32")
            if os.path.exists(fpath):
                return "Windows (Unknown)"
            # Definitely not Windows.
            return None

        try:
            r = os.listdir(fpath)
        except Exception:
            return None

        vers = None
        if len(r) > 0:
            r = sorted(r, reverse=True)
        elif len(r) == 0:
            return "Corrupt Windows Installation"
        vers = r[0]

        for item in self.win_prefixes:
            if vers.startswith(item):
                return self.win_prefixes[item]

        return "Windows (Unknown)"

    def get_windows_bootloader(self, path):
        """ Determine the bootloader version """
        fpath = os.path.join(path, "Boot/BCD")
        if not os.path.exists(fpath):
            return None

        for key in self.win_bootloaders:
            cmd = "grep -qs \"{}\" \"{}\"".format(key, fpath)
            try:
                subprocess.check_call(cmd)
                return self.win_bootloaders[key]
            except Exception:
                continue

        return "Windows bootloader"

    def extract_os_release_key(self, path, find_key):
        """ Grab a key from the given os-release file """
        with open(path, "r") as inp_file:
            for line in inp_file.readlines():
                line = line.replace("\r", "").replace("\n", "").strip()
                if line == "":
                    continue

                if "=" not in line:
                    continue
                splits = line.split("=")
                key = splits[0].lower()
                val = "=".join(splits[1:]).strip()

                if val[0] == "\"":
                    val = val[1:]
                if val[-1] == "\"":
                    val = val[0:-1]

                if key != find_key.lower():
                    continue
                return val
        return None

    def get_linux_version(self, path):
        """ Attempt to get the Linux version string """
        # os-release files, with stateless support
        os_paths = [
            "etc/os-release",
            "usr/lib/os-release"
        ]
        # lsb-release files, with stateless support
        lsb_paths = [
            "etc/lsb-release",
            "usr/lib/lsb-release",
            "usr/share/defaults/etc/lsb-release"
        ]

        key_checks = [
            ("PRETTY_NAME", "NAME", os_paths),
            ("DISTRIB_DESCRIPTION", "DISTRIB_ID", lsb_paths),
        ]

        # Iterate os-release files and then fallback to lsb-release files,
        # respecting stateless heirarchy
        for key_main, key_fallback, paths in key_checks:
            for item in paths:
                fpath = os.path.join(path, item)
                if not os.path.exists(fpath):
                    continue

                pname = self.extract_os_release_key(fpath, key_main)
                if not pname:
                    pname = self.extract_os_release_key(fpath, key_fallback)
                if not pname:
                    continue
                return pname

        return None

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

        # Try Windows first
        # win = self.get_windows_version(mount_point)

        # Unmount again
        if mounted:
            if self.do_umount(mount_point):
                try:
                    os.rmdir(mount_point)
                except Exception as e:
                    print("Failed to remove stagnant directory: %s" % e)
        return None

    def _read_line_complete(self, path):
        with open(path, "r") as inp:
            l = inp.readlines()[0].strip().replace("\r", "").replace("\n", "")
            return l
        return None

    def get_disk_model(self, device):
        """ Get the model of the device """
        node = os.path.basename(device)
        fpath = "/sys/block/{}/device/model".format(node)

        if not os.path.exists(fpath):
            return None
        return self._read_line_complete(fpath)

    def get_disk_vendor(self, device):
        """ Get the vendor for the device """
        node = os.path.basename(device)
        fpath = "/sys/block/{}/device/vendor".format(node)

        if not os.path.exists(fpath):
            return None
        return self._read_line_complete(fpath)

    def format_size(self, size):
        """ Get the *abyte size (not mebibyte) format """
        labels = ["B", "KB", "MB", "GB", "PB", "EB", "ZB", "YB"]

        for i, label in enumerate(labels):
            if size < 1000 or i == len(labels) - 1:
                return size, label
            size = float(size / 1000)

    def format_size_local(self, size, double_precision=False):
        """ Get the locale appropriate representation of the size """
        numeric, code = self.format_size(size)
        fmt = "%.1f" if not double_precision else "%.2f"
        SZ = "%s %s" % (locale.format(fmt, numeric, grouping=True), code)
        return SZ

    def get_disk_size_bytes(self, disk):
        """ Return byte length of disk (parted.Disk) """
        return disk.device.getLength() * disk.device.sectorSize

    def get_disk_size_string(self, disk):
        """ Return formatted size of disk (parted.Disk) """
        return self.format_size_local(self.get_disk_size_bytes(disk))

    def is_efi_booted(self):
        """ Determine if we booted using UEFI """
        return self.is_uefi

    def get_platform_size(self):
        """ 64-bit or 32-bit firmware """
        return self.uefi_fw_size
