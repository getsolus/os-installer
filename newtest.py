#!/usr/bin/env python2.7
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

import sys
import os
from os_installer2.diskman import DiskManager, DriveProber
import parted
import subprocess

def get_partition_length(count, units, device):
    return parted.sizeToSectors(count, units, device.sectorSize)

def get_partition_geometry(device, start, count, units):
    return parted.Geometry(device=device, start=start,
                           length=get_partition_length(count, units, device))

def get_all_remaining_geom(device, start):
    length = device.getLength() - start
    return parted.Geometry(device=device, start=start, length=length)

def format_partition(node, filesystem):
    cmd = None
    if filesystem in ["ext2", "ext3", "ext4"]:
        cmd =  "mkfs.%s -F %s" % (filesystem, node)
    elif filesystem in ["vfat", "fat"]:
        cmd = "mkfs.vfat -t 32 %s" % node
    elif filesystem == "fat12":
        cmd = "mkfs.vfat -F 12 %s" % node
    elif filesystem == "fat16":
        cmd = "mkfs.vfat -F 16 %s" % node
    elif filesystem == "fat32":
        cmd = "mkfs.vfat -F 32 %s" % node
    elif filesystem in ["swap", "linux-swap", "linux-swap(v0)", "linux-swap(v1"]:
        cmd = "mkswap -f %s" % node
    else:
        cmd = "mkfs.%s -F %s" % (filesystem, node)
    try:
        subprocess.check_call(cmd, shell=True)
        return True
    except Exception as e:
        print e

def name_partition_vfat(node, new_label):
    cmd = "/sbin/dosfslabel {} \"{}\"".format(node, new_label)
    try:
        subprocess.check_call(cmd, shell=True)
        return True
    except Exception as e:
        print("Failed to set vfat label: %s" % e)
    return False

def name_partition_ext(node, new_label):
    cmd = "/sbin/e2label {} \"{}\"".format(node, new_label)
    try:
        subprocess.check_call(cmd, shell=True)
        return True
    except Exception as e:
        print("Failed to set ext label: %s" % e)
    return False

def main():
    dm = DiskManager()
    dp = DriveProber(dm)

    dp.probe()

    drive = dp.get_drive("/dev/sdb")

    if not drive.disk:
        print("Drive misses partition table!")
        drive.disk = parted.freshDisk(drive.device, "msdos")

        # Start at 34 for GPT, moar for MBR
        start_offset = drive.disk.getFirstPartition().geometry.end + 1
        print("Starting at %s" % start_offset)

        # create the ESP
        geom = get_partition_geometry(drive.device, start_offset, 512, 'MiB')
        fs = parted.FileSystem(type='fat32', geometry=geom)
        p = parted.Partition(disk=drive.disk, type=parted.PARTITION_NORMAL,
                             fs=fs, geometry=geom)
        p.setFlag(parted.PARTITION_BOOT)

        device = drive.device

        print(drive.disk.maxPartitionStartSector)
        print p.path
        drive.disk.addPartition(p, constraint=device.optimalAlignedConstraint)
        esp = p.path

        # Create a 2GB swap
        old_geom = geom
        geom = get_partition_geometry(drive.device, old_geom.end+1, 2, 'GiB')
        fs = parted.FileSystem(type='linux-swap(v1)', geometry=geom)
        p = parted.Partition(disk=drive.disk, type=parted.PARTITION_NORMAL,
                             fs=fs, geometry=geom)
        drive.disk.addPartition(p, constraint=device.minimalAlignedConstraint)
        swap = p.path

        old_geom = geom

        # Create /
        start = old_geom.end+1
        geom = get_partition_geometry(drive.device, old_geom.end+1, 30, 'GiB')
        fs = parted.FileSystem(type='ext4', geometry=geom)
        p = parted.Partition(disk=drive.disk, type=parted.PARTITION_NORMAL,
                             fs=fs, geometry=geom)

        drive.disk.addPartition(p, constraint=device.optimalAlignedConstraint)
        root = p.path

        # Create home
        old_geom = geom
        geom = get_all_remaining_geom(device, old_geom.end+1)
        fs = parted.FileSystem(type='ext4', geometry=geom)
        p = parted.Partition(disk=drive.disk, type=parted.PARTITION_NORMAL,
                             fs=fs, geometry=geom)

        drive.disk.addPartition(p, constraint=device.optimalAlignedConstraint)
        home = p.path
        print drive.disk.partitions
        drive.disk.commit()

        print("ESP: %s" % esp)
        print("SWAP: %s" % swap)
        print("ROOT: %s" % root)
        print("HOME: %s" % home)

        format_partition(esp, "fat32")
        name_partition_vfat(esp, "EFI SP")
        format_partition(swap, "swap")
        format_partition(root, "ext4")
        format_partition(home, "ext4")
        name_partition_ext(root, "SolusRoot")
        name_partition_ext(home, "SolusHome")
        drive.disk.commit()
    else:
        for partition in drive.disk.partitions:
            drive.disk.removePartition(partition)
        drive.disk.commit()
        drive.device.clobber()
        print("Clobbered")

if __name__ == "__main__":
    if os.geteuid() != 0:
        sys.stderr.write("You must be root to use OsInstaller\n")
        sys.stderr.flush()
        sys.exit(1)
    print("I EAT YOUR DISK. DO NOT RUN ME UNLESS YOU WANT TO LOOSE /dev/sdb!!!")
    print("EXITING BECAUSE YOU ARE NOT IKEY.")
    sys.exit(0)
    main()
