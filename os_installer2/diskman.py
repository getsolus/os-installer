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


class DiskManager:
    """ Manage all disk operations """

    def __init__(self):
        self.scan_parts()

    def scan_parts(self):
        try:
            part_file = open("/proc/partitions")
        except Exception as ex:
            print("Failed to scan parts: %s" % ex)
            return

        for line in part_file.readlines():
            # TODO: Anything useful.
            pass

        part_file.close()
