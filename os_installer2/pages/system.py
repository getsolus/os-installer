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
import re

# This is all we allow. OK.
ValidHostnameRegex = "^[a-z_][a-z0-9_-]*[$]?$"


class InstallerSystemPage(BasePage):
    """ System Settings page. """

    info = None
    host_reg = None
    host_entry = None
    check_utc = None
    error_label = None
    check_boot = None
    combo_boot = None
    # Bootloader issues
    error_label2 = None

    def __init__(self):
        BasePage.__init__(self)
        self.host_reg = re.compile(ValidHostnameRegex)

        wid_group = Gtk.SizeGroup(Gtk.SizeGroupMode.HORIZONTAL)

        mbox = Gtk.VBox(0)
        mbox.set_margin_top(40)
        self.pack_start(mbox, False, False, 0)
        mbox.set_halign(Gtk.Align.CENTER)
        mbox.set_hexpand(False)
        mbox.set_vexpand(False)

        # hostname section
        host = Gtk.Frame()
        host.set_shadow_type(Gtk.ShadowType.NONE)
        host.set_label("What name should this computer use on the network?")
        host.get_label_widget().set_margin_bottom(8)
        mbox.pack_start(host, False, False, 10)

        self.host_entry = Gtk.Entry()
        self.host_entry.connect("changed", self.host_validate)
        self.host_entry.set_placeholder_text("Type the hostname here")
        host.add(self.host_entry)

        self.check_utc = Gtk.CheckButton.new_with_label(
            "System clock uses UTC")
        self.check_utc.set_margin_top(20)
        mbox.pack_start(self.check_utc, False, False, 0)
        self.check_utc.set_no_show_all(True)
        self.check_utc.connect("toggled", self.on_toggled)

        wid_group.add_widget(host)
        wid_group.add_widget(self.check_utc)

        boot = Gtk.Frame()
        boot.set_halign(Gtk.Align.CENTER)
        boot.set_shadow_type(Gtk.ShadowType.NONE)
        self.check_boot = Gtk.CheckButton.new_with_label(
            "Install a bootloader")
        self.check_boot.set_margin_bottom(5)
        self.check_boot.set_margin_top(5)
        boot.set_label_widget(self.check_boot)
        self.combo_boot = Gtk.ComboBoxText()
        boot.add(self.combo_boot)
        self.pack_start(boot, False, False, 0)
        wid_group.add_widget(self.combo_boot)

        self.error_label = Gtk.Label.new("")
        self.error_label.set_valign(Gtk.Align.START)
        self.pack_end(self.error_label, False, False, 0)
        wid_group.add_widget(self.error_label)

        self.error_label2 = Gtk.Label.new("")
        self.error_label2.set_valign(Gtk.Align.START)
        self.pack_end(self.error_label2, False, False, 0)
        wid_group.add_widget(self.error_label2)

    def on_toggled(self, w, d=None):
        """ Handle UTC setting """
        if not self.info:
            return
        self.info.system_utc = w.get_active()

    def host_validate(self, entry):
        """ Validate the hostname """
        text = entry.get_text()
        match = self.host_reg.match(text)
        can_fwd = False
        if match is None:
            entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY,
                                          "action-unavailable-symbolic")
            self.error_label.set_markup(
                "Hostnames must be <b>lowercase</b>, and only contain "
                "<i>letters,\nnumbers, hyphens and underscores</i>."
                "Hostnames must\nalso start with a lowercase letter.")
        else:
            entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY,
                                          "emblem-ok-symbolic")
            self.error_label.set_markup("")
            can_fwd = True
        if not self.info:
            return
        if can_fwd:
            self.info.hostname = text
        else:
            self.info.hostname = None
        self.info.owner.set_can_next(can_fwd)

    def get_title(self):
        return "System Settings"

    def get_name(self):
        return "system-settings"

    def get_icon_name(self):
        return "preferences-other-symbolic"

    def prepare(self, info):
        self.info = info
        dm = self.info.owner.get_disk_manager()
        if dm.is_efi_booted():
            self.check_boot.set_active(True)
            self.check_boot.set_sensitive(False)
            self.check_boot.set_label(
                "Bootloader installation mandatory with UEFI")
        # y u no hostname
        if self.info.windows_present:
            self.check_utc.show()
            self.check_utc.get_child().show()
        else:
            self.check_utc.hide()
        if not self.info.hostname:
            self.info.owner.set_can_next(False)
        else:
            self.info.owner.set_can_next(True)

        self.combo_boot.remove_all()
        options = info.strategy.get_boot_loader_options()
        for loader, id in options:
            self.combo_boot.append(id, loader)
        if len(options) > 0:
            self.combo_boot.set_active(0)
            self.error_label2.set_label("")
            return
        self.set_can_next(False)
        err = info.strategy.get_errors()
        self.error_label2.set_label(
            "Failed to find location for bootloader: {}".format(err))
