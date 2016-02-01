#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
#  
#  Copyright (C) 2013-2016 Ikey Doherty <ikey@solus-project.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#

from configobj import ConfigObj
import os.path


CONFIG_PATH = "/etc/os-installer/install.conf" if os.path.exists("/etc/os-installer/install.conf") else os.path.join(os.getcwd(), "dist/install.conf")

config = ConfigObj(CONFIG_PATH)

DISTRO_NAME = config["Branding"]["Name"]
DISTRO_VERSION = config["Branding"]["Version"]
UI_THEME = config["Branding"]["Theme"]

RESOURCE_DIR = "/usr/share/os-installer" if os.path.exists("/usr/share/os-installer") else os.path.join(os.getcwd(), "data")

