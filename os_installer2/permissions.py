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

import os


class PermissionsManager:

    down_uid = None
    down_gid = None

    def __init__(self):
        if "PKEXEC_UID" in os.environ:
            id_ = os.environ["PKEXEC_UID"]
            try:
                uid = int(id_)
                self.down_uid = uid
                self.down_gid = uid
            except Exception as e:
                print("Defaulting on fallback UID: %s" % e)
            return
        if "SUDO_UID" in os.environ:
            id_ = os.environ["SUDO_UID"]
            try:
                uid = int(id_)
                self.down_uid = uid
                self.down_gid = uid
            except Exception as e:
                print("Defaulting on fallback UID: %s" % e)

    def down_permissions(self):
        """ Drop our current permissions """
        try:
            os.setegid(self.down_gid)
            os.seteuid(self.down_uid)
        except Exception as e:
            print("Failed to drop permissions: %s" % e)
            return False
        return True

    def up_permissions(self):
        """ Elevate our current permissions """
        try:
            os.seteuid(0)
            os.setegid(0)
        except Exception as e:
            print("Failed to raise permissions: %s" % e)
            return False
        return True
