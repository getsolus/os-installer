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


class InstallerUsersPage(BasePage):
    """ User management. """

    info = None

    def __init__(self):
        BasePage.__init__(self)

    def get_title(self):
        return "Who will use this device?"

    def get_name(self):
        return "users"

    def get_icon_name(self):
        return "system-users-symbolic"

    def prepare(self, info):
        self.info = info
        self.info.owner.set_can_next(False)
