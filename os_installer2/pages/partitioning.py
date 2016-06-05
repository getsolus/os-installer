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
from os_installer2.strategy import EmptyDiskStrategy
from os_installer2.strategy import WipeDiskStrategy
from os_installer2.strategy import UseFreeSpaceStrategy
import sys


class InstallerPartitioningPage(BasePage):
    """ Basic location detection page. """

    info = None

    def __init__(self):
        BasePage.__init__(self)

    def get_title(self):
        return "Configure disks"

    def get_name(self):
        return "partitioning"

    def get_icon_name(self):
        return "drive-multidisk-symbolic"

    def prepare(self, info):
        self.info = info

        # Serious sanity stuffs
        if not info.strategy:
            print("FATAL: No strategy")
            sys.exit(0)

        skips = [
            EmptyDiskStrategy,
            WipeDiskStrategy,
            UseFreeSpaceStrategy,
        ]
        for sk in skips:
            if isinstance(info.strategy, sk):
                print("DEBUG: Skippable type")
                self.info.owner.skip_page()
                return
        print("non-skippable strategy: {}".format(info.strategy.get_name()))
