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
from gi.repository import Gtk


class InstallerProgressPage(BasePage):
    """ Actual installation :o """

    info = None

    def __init__(self):
        BasePage.__init__(self)

        lab = Gtk.Label("<big>%s</big>" %
                        "LUCKY FOR YOU THIS ISN'T WORKING YET, RIGHT? "
                        "COULDA LOST AN EYE. OR WORSE, A USB STICK.")
        lab.set_property("xalign", 0.0)
        lab.set_margin_top(40)
        lab.set_use_markup(True)

        lab.set_margin_start(32)

        lab.set_line_wrap(True)
        self.pack_start(lab, False, False, 0)

    def get_title(self):
        return "Installing Solus"

    def get_name(self):
        return "install"

    def get_icon_name(self):
        return "install-symbolic"

    def prepare(self, info):
        self.info = info
        self.info.owner.set_can_next(False)
        self.info.owner.set_can_previous(False)
