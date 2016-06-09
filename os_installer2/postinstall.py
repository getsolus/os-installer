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
        return self.err

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
        p = os.path.join(self.get_installer_target_filesystem(),
                         "home/live")
        if not os.path.exists(p):
            return True
        try:
            shutil.rmtree(p)
        except Exception as e:
            self.set_errors(e)
            return False
        return True
