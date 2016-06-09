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

import subprocess
import shutil
import os


class PostInstallStep:
    """ Basic post-install API """

    # Tracking operations
    info = None

    # Installer reference for doing the hard lifting
    installer = None

    # Errors for this obj
    errors = None

    def __init__(self, info, installer):
        self.info = info
        self.installer = installer

    def apply(self):
        """ Apply this post-install step """
        print("NOT IMPLEMENTED!")
        return False

    def get_display_string(self):
        return "I AM NOT IMPLEMENTED!"

    def set_errors(self, err):
        """ Set the errors for this step """
        self.errors = err

    def get_errors(self):
        """ Get the errors, if any, for this step """
        return self.errors

    def run_in_chroot(self, command):
        """ Helper to enable quick boolean chroot usage """
        full_cmd = "chroot \"{}\" /bin/sh -c \"{}\"".format(
            self.installer.get_installer_target_filesystem(),
            command)
        try:
            subprocess.check_call(full_cmd, shell=True)
        except Exception as e:
            self.set_errors(e)
            return False
        return True

    def is_long_step(self):
        """ Override when this is a long operation and the progressbar should
            pulse, so the user doesn't believe the UI locked up """
        return False


class PostInstallRemoveLiveConfig(PostInstallStep):
    """ Remove the live user from the filesystem """

    def __init__(self, info, installer):
        PostInstallStep.__init__(self, info, installer)

    def get_display_string(self):
        return "Removing live configuration"

    def apply(self):
        # Forcibly remove the user (TODO: Make all this configurable... )
        if not self.run_in_chroot("userdel -fr live"):
            return False
        # Remove sudo
        if not self.run_in_chroot("sed -e '/live ALL=/d' -i /etc/sudoers"):
            return False
        # Make sure home is really gone
        p = os.path.join(self.installer.get_installer_target_filesystem(),
                         "home/live")
        if not os.path.exists(p):
            return True
        try:
            shutil.rmtree(p)
        except Exception as e:
            self.set_errors(e)
            return False
        return True


class PostInstallSyncFilesystems(PostInstallStep):
    """ Just call sync, nothing fancy """

    def __init__(self, info, installer):
        PostInstallStep.__init__(self, info, installer)

    def get_display_string(self):
        return "Flushing buffers to disk.. please wait"

    def is_long_step(self):
        return True

    def apply(self):
        try:
            subprocess.check_call("sync", shell=True)
        except:
            pass
        return True


class PostInstallMachineID(PostInstallStep):
    """ Initialise the machine-id """

    def __init__(self, info, installer):
        PostInstallStep.__init__(self, info, installer)

    def get_display_string(self):
        return "Creating machine-id for new installation"

    def apply(self):
        fp = os.path.join(self.installer.get_installer_target_filesystem(),
                          "etc/machine-id")
        # Delete existing machine-id
        if os.path.exists(fp):
            try:
                os.remove(fp)
            except Exception as e:
                self.set_errors(e)
                return False

        # Now create a new machine-id
        if not self.run_in_chroot("systemd-machine-id-setup"):
            self.set_errors("Failed to construct machine-id")
            return False
        return True


# We use this guy to set the global layout..
KEYBOARD_CONFIG_TEMPLATE = """
# Read and parsed by systemd-localed. It's probably wise not to edit this file
# manually too freely.
Section "InputClass"
        Identifier "system-keyboard"
        MatchIsKeyboard "on"
        Option "XkbModel" "%(XKB_MODEL)s"
        Option "XkbLayout" "%(XKB_LAYOUT)s"
EndSection
"""


class PostInstallKeyboard(PostInstallStep):
    """ Set the keyboard layout on the target device """

    def __init__(self, info, installer):
        PostInstallStep.__init__(self, info, installer)

    def get_display_string(self):
        return "Storing keyboard configuration"

    def apply(self):
        xkb_model = "pc104"
        x11dir = os.path.join(self.installer.get_installer_target_filesystem(),
                              "etc/X11/xorg.conf.d")
        x11file = os.path.join(x11dir, "00-keyboard.conf")

        # create the x11 dir
        if not os.path.exists(x11dir):
            try:
                os.makedirs(x11dir, 0o0755)
            except Exception as ex:
                self.set_errors(ex)
                return False

        # set up the template
        tmpl = KEYBOARD_CONFIG_TEMPLATE % {
            'XKB_MODEL': xkb_model, 'XKB_LAYOUT': self.info.keyboard
        }

        # write the template to disk
        tmpl = tmpl.strip() + "\n"
        try:
            with open(x11file, "w") as xfile:
                os.chmod(x11file, 0o0644)
                xfile.write(tmpl)
        except Exception as ex:
            self.set_errors(ex)
            return False
        return True


class PostInstallLocale(PostInstallStep):
    """ Set the system locale """

    def __init__(self, info, installer):
        PostInstallStep.__init__(self, info, installer)

    def get_display_string(self):
        return "Storing system locale"

    def apply(self):
        lang = self.info.locale

        # Dump to locale.conf
        fpath = os.path.join(self.installer.get_installer_target_filesystem(),
                             "etc/locale.conf")
        try:
            with open(fpath, "w") as localef:
                if not lang.endswith(".utf8"):
                    lc = lang.split(".")[0]
                    lang = "{}.utf8".format(lc)
                localef.write("LANG={}\n".format(lang))
        except Exception as e:
            self.set_errors(e)
            return False
        return True


ADJTIME_LOCAL = """
0.0 0 0.0
0
LOCAL
"""


class PostInstallTimezone(PostInstallStep):
    """ Set up the timezone """

    def __init__(self, info, installer):
        PostInstallStep.__init__(self, info, installer)

    def get_display_string(self):
        return "Storing system timezone"

    def apply(self):
        """ Link /etc/localtime up to zoneinfo """
        loc = self.info.timezone
        self.run_in_chroot("rm -f /etc/localtime")
        cmd = "ln -sf \"/usr/share/zoneinfo/{}\" /etc/localtime".format(loc)
        if not self.run_in_chroot(cmd):
            self.set_errors("Failed to set timezone")
            return False

        if not self.info.windows_present:
            return True

        # Set adjtime to local for Windows users
        adjp = os.path.join(self.installer.get_installer_target_filesystem(),
                            "etc/adjtime")
        try:
            with open(adjp, "w") as adjtime:
                adjtime.write(ADJTIME_LOCAL.strip() + "\n")
        except Exception as e:
            print("Warning: Failed to update adjtime: {}".format(e))
        return True


class PostInstallUsers(PostInstallStep):
    """ Add users to the new installation """

    normal_groups = None
    admin_groups = None

    def __init__(self, info, installer):
        PostInstallStep.__init__(self, info, installer)

        self.normal_groups = [
            "audio,"
            "video",
            "cdrom",
            "dialout",
            "fuse"
        ]
        self.admin_groups = [
            "sudo",
            "lpadmin"
        ]

    def get_display_string(self):
        return "Creating users"

    def apply(self):
        """ Add all of the system users """

        pwd_file = []

        # Add all the users.
        for user in self.info.users:
            groups = []
            groups.extend(self.normal_groups)
            if user.admin:
                groups.extend(self.admin_groups)

            cmd = "useradd -s {} -c '{}' -G {} {}".format(
                "/bin/bash",  # Default shell in Solus
                user.realname,
                ",".join(groups),
                user.username)

            try:
                self.run_in_chroot(cmd)
            except Exception as e:
                self.set_errors("Cannot configure user: {}".format(e))
                return False

            pwd_file.append("{}:{}".format(user.username, user.password))

        f = os.path.join(self.installer.get_installer_target_filesystem(),
                         "tmp/newusers.conf")

        # Pass off the passwords to chpasswd
        pwds_done = False
        try:
            with open(f, "w") as pwds:
                pwds.write("\n".join(pwd_file))

                self.run_in_chroot("cat /tmp/newusers.conf | chpasswd")
                os.remove(f)
                pwds_done = True
        except Exception as e:
            self.set_errors("Unable to update passwords: {}".format(e))

        if not pwds_done:
            try:
                os.remove(f)
            except:
                pass
            return False

        # Disable the root account
        if not self.run_in_chroot("passwd -d root"):
            self.set_errors("Failed to disable root account")
            return False
        return True
