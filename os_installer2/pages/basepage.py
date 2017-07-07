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

from gi.repository import Gtk


class BasePage(Gtk.VBox):
    """ Base widget for all page implementations to save on duplication. """

    def __init__(self):
        Gtk.VBox.__init__(self)

    def get_title(self):
        return None

    def get_name(self):
        return None

    def get_icon_name(self):
        return "dialog-error"

    def get_primary_answer(self):
        return None

    def prepare(self, info):
        pass

    def seed(self, setup):
        pass

    def is_hidden(self):
        return False

    def do_expensive_init(self):
        """ Do expensive startup tasks outside of the main thread """
        pass
