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


class FramedHeader(Gtk.Frame):
    """ Summary header widget """

    vbox = None

    def __init__(self, icon_name, title):
        Gtk.Frame.__init__(self)
        box = Gtk.HBox(0)

        sz = Gtk.IconSize.DIALOG
        image = Gtk.Image.new_from_icon_name(icon_name, sz)
        box.pack_start(image, False, False, 0)

        image.set_property("margin", 10)
        image.set_valign(Gtk.Align.START)

        label = Gtk.Label("<big>{}</big>".format(title))
        label.set_use_markup(True)
        box.pack_start(label, False, False, 0)
        label.set_halign(Gtk.Align.START)
        label.set_valign(Gtk.Align.START)
        label.set_property("margin", 10)

        self.vbox = Gtk.VBox(0)
        box.pack_end(self.vbox, False, False, 0)
        self.vbox.set_property("margin", 10)

        self.add(box)

    def add_label(self, label):
        self.vbox.pack_start(label, False, False, 2)
        label.show_all()


class InstallerSummaryPage(BasePage):
    """ Installer summary page. """

    locale_details = None
    install_details = None
    system_details = None
    user_details = None

    def __init__(self):
        BasePage.__init__(self)

        scroll = Gtk.ScrolledWindow(None, None)
        scroll.set_border_width(40)
        scroll.set_margin_top(20)
        self.pack_start(scroll, True, True, 0)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        items = Gtk.VBox(0)
        scroll.add(items)
        scroll.set_overlay_scrolling(False)
        self.locale_details = FramedHeader(
            "preferences-desktop-locale-symbolic",
            "Language &amp; Region")
        items.pack_start(self.locale_details, False, False, 2)

        self.install_details = FramedHeader("drive-harddisk-system-symbolic",
                                            "Installation")
        items.pack_start(self.install_details, False, False, 2)

        self.user_details = FramedHeader("system-users-symbolic", "Users")
        items.pack_start(self.user_details, False, False, 2)

        self.system_details = FramedHeader("preferences-other-symbolic",
                                           "System Details")
        items.pack_start(self.system_details, False, False, 2)

    def get_title(self):
        return "Summary"

    def get_name(self):
        return "summary"

    def get_icon_name(self):
        return "mail-mark-important-symbolic"

    def _clean_label(self, label):
        lab = Gtk.Label(label)
        lab.set_halign(Gtk.Align.START)
        return lab

    def prepare(self, info):
        info.owner.set_final_step(True)

        # First up, region stuff
        for kid in self.locale_details.vbox.get_children():
            kid.destroy()

        self.locale_details.add_label(self._clean_label(
            "Use {} as system language".format(info.locale_sz)))
        self.locale_details.add_label(self._clean_label(
            "Use {} as default keyboard layout".format(info.keyboard_sz)))
        self.locale_details.add_label(self._clean_label(
            "Set timezone to {}".format(info.timezone)))

        # Details
        for kid in self.system_details.vbox.get_children():
            kid.destroy()
        self.system_details.add_label(self._clean_label(
            "Set device host-name to \"{}\"".format(info.hostname)))
        if info.windows_present:
            s = "Enable UTC time" if info.system_utc else "Disable UTC time"
            self.system_details.add_label(self._clean_label(s))
