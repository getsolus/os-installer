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

from gi.repository import Gtk


class BasePage(Gtk.Box):
    """ Base widget for all page implementations to save on duplication. """

    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL, spacing=0)

        mk = u"<span font-size='x-large'>{}</span>".format(self.get_title())
        lab = Gtk.Label.new(mk)
        lab.set_property("margin-top", 10)
        lab.set_property("margin-start", 20)
        lab.set_property("margin-bottom", 10)
        lab.set_use_markup(True)
        lab.set_halign(Gtk.Align.START)
        self.pack_start(lab, False, False, 0)

        sep = Gtk.Separator.new(Gtk.Orientation.HORIZONTAL)
        self.pack_start(sep, False, False, 0)

    def get_title(self):
        return None

    def get_sidebar_title(self):
        return "Not implemented.."

    def get_name(self):
        return None

    def get_icon_name(self, plasma=False):
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
