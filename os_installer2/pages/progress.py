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

from .basepage import BasePage
from gi.repository import Gtk, GLib, Pango
import threading
import time
from collections import OrderedDict
from os_installer2 import SOURCE_FILESYSTEM, INNER_FILESYSTEM
from os_installer2.diskops import DiskOpCreateDisk, DiskOpResizeOS
from os_installer2.diskops import DiskOpCreatePartition
from os_installer2.diskops import DiskOpFormatPartition
from os_installer2.postinstall import PostInstallRemoveLiveConfig
from os_installer2.postinstall import PostInstallSyncFilesystems
from os_installer2.postinstall import PostInstallMachineID
from os_installer2.postinstall import PostInstallKeyboard
from os_installer2.postinstall import PostInstallLocale
from os_installer2.postinstall import PostInstallTimezone
import os
import stat
import parted


# Update 5 times a second, vs every byte copied..
UPDATE_FREQUENCY = 1000 / 5


class InstallerProgressPage(BasePage):
    """ Actual installation :o """

    info = None
    progressbar = None
    label = None
    had_start = False
    installing = False
    mount_tracker = None
    temp_dirs = None

    # Our disk manager
    dm = None

    # Current string for the idle monitor to display in Gtk thread
    display_string = None

    # How much we need to copy
    filesystem_source_size = 0
    filesystem_copied_size = 0
    filesystem_copying = False

    # Enabled post-install steps
    post_install_enabled = None

    # Are we in the post stage ?
    in_postinstall = False
    post_install_current = 0

    # Initialised post installs
    post_installs = None
    # Long-ass steps should pulse...
    should_pulse = False

    def __init__(self):
        BasePage.__init__(self)

        box = Gtk.VBox(0)
        box.set_border_width(20)
        self.pack_end(box, False, False, 0)

        self.label = Gtk.Label("Initializing installer")
        self.label.set_max_width_chars(250)
        self.label.set_ellipsize(Pango.EllipsizeMode.END)
        self.label.set_halign(Gtk.Align.START)
        box.pack_start(self.label, True, True, 2)

        self.progressbar = Gtk.ProgressBar()
        box.pack_start(self.progressbar, False, False, 2)

        self.mount_tracker = OrderedDict()
        self.temp_dirs = []

        self.post_install_enabled = [
            PostInstallSyncFilesystems,
            PostInstallRemoveLiveConfig,
            PostInstallMachineID,
            PostInstallKeyboard,
            PostInstallLocale,
            PostInstallTimezone,
        ]
        # Active postinstalls..
        self.post_installs = []

    def get_title(self):
        return "Installing Solus"

    def get_name(self):
        return "install"

    def get_icon_name(self):
        return "install-symbolic"

    def begin_install(self):
        """ Begin the real work of doing the installation """
        # We don't yet do anything...
        self.label.set_markup("Warming up")

        self.installing = True
        # Hook up the idle monitor
        GLib.timeout_add(UPDATE_FREQUENCY, self.idle_monitor)
        t = threading.Thread(target=self.install_thread)
        t.start()

    def get_display_string(self):
        """ Ensure duped access for display string (threading..) """
        return str(self.display_string)

    def set_display_string(self, sz):
        """ Set the current display string """
        self.display_string = sz
        if not self.filesystem_copying:
            print(sz)

    def idle_monitor(self):
        """ Called periodicially so we can update our view """
        self.label.set_markup(self.get_display_string())
        if self.filesystem_copying:
            cp = float(self.filesystem_copied_size)
            tot = float(self.filesystem_source_size)
            if cp < tot and cp > 0:
                fraction = cp / tot
                self.progressbar.set_fraction(fraction)
            else:
                self.progressbar.pulse()
        elif self.in_postinstall:
            cur = float(self.post_install_current)
            tot = float(len(self.post_installs))
            if cur < tot and cur > 0 and not self.should_pulse:
                fraction = cur / tot
                self.progressbar.set_fraction(fraction)
            else:
                self.progressbar.pulse()
        else:
            self.progressbar.pulse()

        if not self.installing:
            print("Finished idle_monitor")
        return self.installing

    def prepare(self, info):
        self.info = info
        self.dm = info.owner.get_disk_manager()
        self.info.owner.set_can_next(False)
        self.info.owner.set_can_previous(False)
        self.info.owner.set_can_quit(False)

        if not self.had_start:
            self.had_start = True
            self.begin_install()

    def _mkdtemp(self, suffix='installer'):
        """ Create and track the temporary directory """
        d = self.dm.create_temp_dir()
        if not d:
            return None
        self.temp_dirs.append(d)
        return d

    def get_mount_point_for(self, node):
        """ Get the mount point of a given node """
        if node in self.mount_tracker:
            return self.mount_tracker[node]
        return None

    def mount_source_filesystem(self):
        """ Mount the source and child """
        source = self._mkdtemp()
        inner_path = os.path.join(source, INNER_FILESYSTEM)
        if not source:
            self.set_display_string("Cannot mkdtemp")
            return False

        # Try to mount the squashfs
        if not self.dm.do_mount(SOURCE_FILESYSTEM, source, "auto", "loop"):
            self.set_display_string("Cannot mount source filesystem")
            return False
        self.mount_tracker[SOURCE_FILESYSTEM] = source

        # See if the kid exists or not
        if not os.path.exists(inner_path):
            self.set_display_string("Cannot find {}".format(inner_path))
            return False

        inner_child = self._mkdtemp()
        # Try to mount the kid to a new temp
        if not inner_child:
            self.set_display_string("Cannot mkdtemp")
            return False
        if not self.dm.do_mount(inner_path, inner_child, "auto", "loop"):
            self.set_display_string("Cannot mount inner child")
            return False
        self.mount_tracker[INNER_FILESYSTEM] = inner_child

        # Now grab the size of the source filesystem
        try:
            vfs = os.statvfs(inner_child)
            size = (vfs.f_blocks - vfs.f_bfree) * vfs.f_frsize
            self.filesystem_source_size = size
        except Exception as e:
            self.set_display_string("Cannot compute source size: {}".format(e))
            return False

        return True

    def unmount_all(self):
        """ umount everything we've mounted """
        ret = True

        self.set_display_string("Unmounting filesystems - might take a while")

        # Visit in reverse order
        keys = self.mount_tracker.keys()
        keys.reverse()
        for key in keys:
            if not self.dm.do_umount(self.mount_tracker[key]):
                self.set_display_string("Cannot umount {}".format(key))
                ret = False

        for tmp in self.temp_dirs:
            try:
                os.rmdir(tmp)
            except Exception as e:
                self.set_display_string("Cannot rmdir {}: {}".format(
                    tmp, e))
                ret = False
        return ret

    def do_copy_file(self, source, dest):
        """ Simply copy a file .. """
        input = None
        dst = None

        try:
            BUF_SIZE = 16 * 1024
            input = open(source, "rb")
            dst = open(dest, "wb")
            while (True):
                read = input.read(BUF_SIZE)
                if not read:
                    break
                self.filesystem_copied_size += len(read)
                dst.write(read)
            input.close()
            dst.close()
            return True
        except Exception as ex:
            self.set_display_string(ex)
            if input:
                input.close()
            if dst:
                dst.close()
        return False

    def get_installer_target_filesystem(self):
        """ Get the mount point for the root partition for post-install """
        root = self.info.strategy.get_root_partition()
        root_fs = self.get_mount_point_for(root)
        return root_fs

    def get_installer_source_filesystem(self):
        """ Get the mount point for the source filesystem for post-install """
        source_fs = self.get_mount_point_for(INNER_FILESYSTEM)
        return source_fs

    def copy_system(self):
        """ Attempt to copy the entire filesystem across """
        print("Need to copy {} bytes".format(self.filesystem_source_size))

        source_fs = self.get_mount_point_for(INNER_FILESYSTEM)
        if not source_fs:
            return False
        root = self.info.strategy.get_root_partition()
        root_fs = self.get_mount_point_for(root)
        if not root_fs:
            self.set_display_string("Missing rootfs")
            return False

        self.filesystem_copying = True

        # Ensure we don't follow links, i.e. we're never in a situation where
        # we're creating broken leading directories
        for root, dirs, files in os.walk(source_fs,
                                         topdown=False,
                                         followlinks=False):
            # Mend the root to allow source/target use
            dir_root = root
            if dir_root.startswith(source_fs):
                dir_root = dir_root[len(source_fs):]
                if len(dir_root) > 0 and dir_root[0] != '/':
                    dir_root = "/" + dir_root

            # Create the container directory first
            target_dir = os.path.join(root_fs, dir_root[1:])
            if not os.path.exists(target_dir):
                try:
                    # We set the permissions up properly later
                    os.makedirs(target_dir, 0o0755)
                except Exception as ex:
                    self.set_display_string("Cannot create dir: {}".format(ex))
                    return False

            # Walk the tree from the back to restore permissions properly
            for f in files:
                source_path = os.path.join(source_fs, dir_root[1:], f)
                target_path = os.path.join(root_fs, dir_root[1:], f)

                # Not really necessary but meh
                self.set_display_string("Copying {}".format(
                    os.path.join(dir_root, f)))

                try:
                    st = os.lstat(source_path)
                    mode = stat.S_IMODE(st.st_mode)
                    is_link = False
                    is_copied = False

                    if stat.S_ISLNK(st.st_mode):
                        linkto = os.readlink(source_path)
                        os.symlink(linkto, target_path)
                        is_link = True
                    elif stat.S_ISCHR(st.st_mode):
                        os.mknod(target_path, stat.S_IFCHR | mode, st.st_rdev)
                    elif stat.S_ISBLK(st.st_mode):
                        os.mknod(target_path, stat.S_IFBLK | mode, st.st_rdev)
                    elif stat.S_ISFIFO(st.st_mode):
                        os.mknod(target_path, stat.S_IFIFO | mode)
                    elif stat.S_ISSOCK(st.st_mode):
                        os.mknod(target_path, stat.S_IFSOCK | mode)
                    elif stat.S_ISREG(st.st_mode):
                        is_copied = True
                        if not self.do_copy_file(source_path, target_path):
                            return False

                    # Chown it.
                    os.lchown(target_path, st.st_uid, st.st_gid)
                    if not is_link:
                        # Copy permissiions/utime
                        os.chmod(target_path, mode)
                        os.utime(target_path, (st.st_atime, st.st_mtime))
                    # copy_file handles size
                    if not is_copied:
                        self.filesystem_copied_size += st.st_size

                except Exception as ex:
                    self.set_display_string("Failed to copy {}".format(
                        source_path))
                    return False

            # Chown/utime the dirs as we come out, meaning we set perms/time
            # on everything but / itself
            for d in dirs:
                try:
                    target_path = os.path.join(root_fs, dir_root[1:], d)
                    source_path = os.path.join(source_fs, dir_root[1:], d)
                    self.set_display_string("Creating: {}".format(
                        os.path.join(dir_root, d)))
                    st = os.lstat(source_path)
                    mode = stat.S_IMODE(st.st_mode)
                    if not stat.S_ISDIR(st.st_mode):
                        linkto = os.readlink(source_path)
                        os.symlink(linkto, target_path)
                        os.lchown(target_path, st.st_uid, st.st_gid)
                        continue

                    os.chown(target_path, st.st_uid, st.st_gid)
                    os.chmod(target_path, mode)
                    os.utime(target_path, (st.st_atime, st.st_mtime))
                    # Update progress
                    self.filesystem_copied_size += st.st_size
                except Exception as ex:
                    self.set_display_string("Permissions issue: {}".format(ex))
                    return False

        self.set_display_string("Finalizing file copy")
        return True

    def wait_disk(self, op):
        """ Wait for the disk to become available """
        p = op.part.path

        self.set_display_string("Verifying existence of {}".format(p))
        count = 0
        while (count < 5):
            if os.path.exists(p):
                return True
            self.set_display_string("Waiting for {}".format(p))
            time.sleep(0.5)
            count += 1
        if not os.path.exists(p):
            self.set_display_string("Couldn't locate {}".format(p))
            return False
        return True

    def apply_disk_strategy(self, simulate):
        """ Attempt to apply the given disk strategy """
        strategy = self.info.strategy
        ops = strategy.get_operations()

        table_ops = [x for x in ops if isinstance(x, DiskOpCreateDisk)]
        resizes = [x for x in ops if isinstance(x, DiskOpResizeOS)]
        if len(table_ops) > 1:
            self.set_display_string("Wiping disk more than once, error")
            return False
        if len(resizes) > 1:
            self.set_display_string("Multiple resizes not supported")
            return False

        # Madman time: Go apply the operations. *Gulp*
        disk = strategy.disk
        if disk and simulate:
            disk = disk.duplicate()

        part_offset = 0
        part_step = parted.sizeToSectors(16, 'kB', strategy.device.sectorSize)
        if disk:
            # Start at the very beginning of the disk, we don't
            # support free-space installation
            part_offset = disk.getFirstPartition().geometry.end + part_step

        for op in ops:
            self.set_display_string(op.describe())
            op.set_part_offset(part_offset)
            if not op.apply(disk, simulate):
                er = op.get_errors()
                if not er:
                    er = "Failed to apply operation: {}".format(op.describe())
                self.set_display_string(er)
                return False
            # If it created a disk, go use it.
            if isinstance(op, DiskOpCreateDisk):
                disk = op.disk
                # Now set the part offset
                part_offset = disk.getFirstPartition().geometry.end + part_step
            elif isinstance(op, DiskOpResizeOS):
                part_offset = op.new_part_off + part_step
            elif isinstance(op, DiskOpCreatePartition):
                # Push forward the offset
                part_offset = op.part_end + part_step

        if simulate:
            return True

        try:
            disk.commit()
        except Exception as e:
            self.set_display_string("Failed to update disk: {}".format(e))
            return False

        try:
            os.system("sync")
        except:
            pass

        # Post-process, format all the things
        for op in ops:
            if isinstance(op, DiskOpCreatePartition):
                # Wait for device to show up!
                if not self.wait_disk(op):
                    return False
                if not op.apply_format(disk):
                    e = op.get_errors()
                    self.set_display_string(
                        "Failed to apply format: {}".format(e))
                    return False
            elif isinstance(op, DiskOpFormatPartition):
                if not op.apply(disk):
                    e = op.get_errors()
                    self.set_display_string(
                        "Failed to apply format: {}".format(e))
                    return False
            else:
                continue
        return True

    def mount_target_filesystem(self):
        """ Mount our target filesystem(s) """
        strategy = self.info.strategy

        root = strategy.get_root_partition()
        if not root or root.strip() == "":
            self.set_display_string("Fatal: Missing root partition")
            return False
        target = self._mkdtemp()
        if not target:
            self.set_display_string("Cannot create temporary root directory")
            return False
        if not self.dm.do_mount(root, target, "auto", "rw"):
            self.set_display_string("Cannot mount root partition")
            return False
        self.mount_tracker[root] = target

        print("DEBUG: / ({}) mounted at {}".format(root, target))
        # TODO: Mount home if it is needed
        return True

    def install_thread(self):
        """ Handle the real work of installing =) """
        self.set_display_string("Analyzing installation configuration")

        # immediately gain privs
        self.info.owner.get_perms_manager().up_permissions()

        # Simulate!
        self.set_display_string("Simulating disk operations")
        if not self.apply_disk_strategy(True):
            self.installing = False
            self.set_display_string("Failed to simulate disk strategy")
            return False

        # Now do it for real.
        if not self.apply_disk_strategy(False):
            self.installing = False
            self.set_display_string("Failed to apply disk strategy")
            return False

        # Now mount up as it were.
        if not self.mount_source_filesystem():
            self.unmount_all()
            self.set_display_string("Failed to mount!")
            self.installing = False
            return False

        # TODO: Mount target filesystem
        if not self.mount_target_filesystem():
            self.unmount_all()
            self.set_display_string("Failed to mount target!")
            self.installing = False
            return False

        # Copy source -> target
        if not self.copy_system():
            self.filesystem_copying = False
            self.set_display_string("Failed to copy filesystem")
            self.unmount_all()
            self.installing = False
            return False
        self.filesystem_copying = False

        time.sleep(1)
        self.set_display_string("Initializing post-installs")
        for ptype in self.post_install_enabled:
            r = ptype(self.info, self)
            self.set_display_string("Initialised {}".format(
                r.get_display_string()))
            self.post_installs.append(r)

        # Now run the post-installs
        self.in_postinstall = True
        for step in self.post_installs:
            self.should_pulse = step.is_long_step()
            disp = step.get_display_string()
            self.set_display_string(disp)
            try:
                b = step.apply()
                if not b:
                    self.set_display_string(step.get_errors())
            except Exception as e:
                b = False
                self.set_display_string(e)
            if not b:
                self.set_display_string(step.get_errors())
                # Failed :(
                self.in_postinstall = False
                self.unmount_all()
                self.installing = False
                return False
            self.post_install_current += 1

        # Actually made it. :o
        self.in_postinstall = False

        # Ensure the idle monitor stops
        if not self.unmount_all():
            self.set_display_string("Failed to unmount cleanly!")

        self.installing = False
