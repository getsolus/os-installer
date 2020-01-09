#!/bin/true
# -*- coding: utf-8 -*-
#
#  This file is part of os-installer
#
#  Copyright 2013-2020 Solus <copyright@getsol.us>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#

import gi.repository
import os
import locale
gi.require_version('Gtk', '3.0')
gi.require_version('Gio', '2.0')
gi.require_version('GnomeDesktop', '3.0')
gi.require_version('TimezoneMap', '1.0')


# The path of the source filesystem
SOURCE_FILESYSTEM = "/run/initramfs/live/LiveOS/squashfs.img"

# The guy inside that is actually our filesystem to copy
INNER_FILESYSTEM = "LiveOS/rootfs.img"

# Absolute minimum size
MB = 1000 * 1000
GB = 1000 * MB
MIN_REQUIRED_SIZE = 10 * GB


def get_resource_path():
    bsPath = os.path.dirname(__file__)
    return os.path.join(bsPath, "data")


def join_resource_path(path):
    return os.path.join(get_resource_path(), path)


def format_size(size):
    """ Get the *abyte size (not mebibyte) format """
    labels = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]

    for i, label in enumerate(labels):
        if size < 1000 or i == len(labels) - 1:
            return size, label
        size = float(size / 1000)


def format_size_local(size, double_precision=False):
    """ Get the locale appropriate representation of the size """
    numeric, code = format_size(size)
    fmt = "%.1f" if not double_precision else "%.2f"
    SZ = "{} {}".format(locale.format(fmt, numeric, grouping=True), code)
    return SZ
