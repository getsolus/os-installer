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


class InstallerLanguagePage(BasePage):
    """ Basic language page. """

    def __init__(self):
        BasePage.__init__(self)

    def get_title(self):
        return "Choose a language"

    def get_name(self):
        return "language"

    def get_icon_name(self):
        return "preferences-desktop-locale-symbolic"
