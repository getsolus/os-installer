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

        self.title = Gtk.Label("<span font-size='xx-large'>%s</span>" %
                               self.get_title())
        self.title.set_use_markup(True)

        self.image = Gtk.Image()
        self.image.set_from_icon_name(self.get_icon_name(),
                                      Gtk.IconSize.DIALOG)
        self.image.set_padding(10, 10)

        header = Gtk.HBox()
        header.pack_start(self.image, False, False, 0)
        header.pack_start(self.title, False, False, 0)

        header.get_style_context().add_class("primary-toolbar")

        self.pack_start(header, False, True, 0)
        self.image.set_margin_start(20)
        self.title.set_margin_start(10)

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
