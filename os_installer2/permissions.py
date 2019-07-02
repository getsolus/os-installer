#!/bin/true
# -*- coding: utf-8 -*-
#
#  This file is part of os-installer
#
#  Copyright 2013-2019 Solus <copyright@getsol.us>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#

import os
import pwd


class PermissionsManager:

    down_uid = None
    down_gid = None
    home_dir = None

    def __init__(self):
        if "PKEXEC_UID" in os.environ:
            id_ = os.environ["PKEXEC_UID"]
            try:
                uid = int(id_)
                self.down_uid = uid
                self.down_gid = uid
                self.set_details()
            except Exception as e:
                print("Defaulting on fallback UID: {}".format(e))
            return
        if "SUDO_UID" in os.environ:
            id_ = os.environ["SUDO_UID"]
            try:
                uid = int(id_)
                self.down_uid = uid
                self.down_gid = uid
                self.set_details()
            except Exception as e:
                print("Defaulting on fallback UID: {}".format(e))

    def set_details(self):
        pw = pwd.getpwuid(self.down_uid)
        if not pw:
            self.home_dir = "/home/live"
            return
        self.home_dir = pw.pw_dir

    def down_permissions(self):
        """ Drop our current permissions """
        try:
            os.setresgid(self.down_gid, self.down_gid, 0)
            os.setresuid(self.down_uid, self.down_uid, 0)
            os.environ['HOME'] = self.home_dir
        except Exception as e:
            print("Failed to drop permissions: {}".format(e))
            return False
        return True

    def up_permissions(self):
        """ Elevate our current permissions """
        try:
            os.setresuid(0, 0, 0)
            os.setresgid(0, 0, 0)
            os.environ['HOME'] = '/root'
        except Exception as e:
            print("Failed to raise permissions: {}".format(e))
            return False
        return True
