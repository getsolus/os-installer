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
from os_installer2.users import User, USERNAME_REGEX
import re

LABEL_COLUMN = 0
DATA_COLUMN = 1


class UserPanel(Gtk.VBox):
    """Userpanel. Represents a user. Whoda thunk it. """

    def __init__(self, user):
        Gtk.VBox.__init__(self)

        self.user = user

        label = Gtk.Label("<big>{}</big> - {}".format(
            self.user.realname,
            self.user.username))
        label.set_use_markup(True)
        label_details = Gtk.Label("")
        details = ""

        if self.user.autologin:
            details += "     - {}".format(
                "will be automatically logged into the computer")
        else:
            details += "     - {}".format(
                "will use a password to log into the computer")
        if self.user.admin:
            details += "\n     - {}".format(
                "will have administrative capabilities")
        else:
            details += "\n     - {}".format("will be an ordinary user")

        label_details.set_markup(details)
        label.set_halign(Gtk.Align.START)
        label_details.set_halign(Gtk.Align.START)
        self.pack_start(label, True, True, 4)
        self.pack_start(label_details, False, False, 0)


class NewUserPage(Gtk.Grid):
    """ Form for creating a new user """

    uname_field = None
    rname_field = None
    pword_field = None
    pword_field2 = None

    def validator(self, entry):
        pass

    def update_score(self, widget, score):
        """ Update the score for validation """
        if widget not in self.scores:
            self.scores[widget] = score
        else:
            self.scores[widget] = score

        total_score = len([i for i in self.scores.values() if i])
        self.ok.set_sensitive(total_score == self.needed_score)

    def __init__(self, owner):
        Gtk.Grid.__init__(self)
        self.owner = owner

        self.set_column_spacing(10)
        self.set_row_spacing(10)
        self.set_margin_left(50)
        self.set_margin_right(50)

        self.scores = dict()
        self.needed_score = 4

        self.username_regex = re.compile(USERNAME_REGEX)

        row = 0
        uname_label = Gtk.Label("Username:")
        self.uname_field = Gtk.Entry()
        self.uname_field.set_hexpand(True)
        self.uname_field.connect("changed", self.validator)
        self.attach(uname_label, LABEL_COLUMN, row, 1, 1)
        self.attach(self.uname_field, DATA_COLUMN, row, 1, 1)

        row += 1
        rname_label = Gtk.Label("Real name:")
        self.rname_field = Gtk.Entry()
        self.rname_field.connect("changed", self.validator)
        self.attach(rname_label, LABEL_COLUMN, row, 1, 1)
        self.attach(self.rname_field, DATA_COLUMN, row, 1, 1)

        row += 1
        pword_label = Gtk.Label("Password:")
        self.pword_field = Gtk.Entry()
        self.pword_field.set_visibility(False)
        self.pword_field.connect("changed", self.validator)
        self.attach(pword_label, LABEL_COLUMN, row, 1, 1)
        self.attach(self.pword_field, DATA_COLUMN, row, 1, 1)

        row += 1
        pword_label2 = Gtk.Label("Confirm password:")
        self.pword_field2 = Gtk.Entry()
        self.pword_field2.connect("changed", self.validator)
        self.pword_field2.set_visibility(False)
        self.attach(pword_label2, LABEL_COLUMN, row, 1, 1)
        self.attach(self.pword_field2, DATA_COLUMN, row, 1, 1)

        row += 1
        # And now an administrative user check
        self.adminuser = Gtk.CheckButton(
            "This user should have administrative capabilities")
        self.attach(self.adminuser, DATA_COLUMN, row, 1, 1)

        row += 1
        btnbox = Gtk.ButtonBox()
        btnbox.set_spacing(5)
        # Lastly the action buttons
        self.ok = Gtk.Button("Add now")
        self.ok.get_style_context().add_class("suggested-action")
        ok_image = Gtk.Image()
        ok_image.set_from_icon_name("list-add-symbolic", Gtk.IconSize.BUTTON)
        self.ok.set_image(ok_image)
        self.ok.set_sensitive(False)
        self.ok.connect("clicked", self.add_user)

        self.cancel = Gtk.Button("Cancel")
        self.cancel.connect("clicked", lambda x: self.owner.show_main())
        cancel_image = Gtk.Image()
        cancel_image.set_from_icon_name("window-close-symbolic",
                                        Gtk.IconSize.BUTTON)
        self.cancel.set_image(cancel_image)

        btnbox.set_layout(Gtk.ButtonBoxStyle.START)
        btnbox.set_margin_top(10)
        btnbox.add(self.ok)
        btnbox.add(self.cancel)
        self.attach(btnbox, DATA_COLUMN, row, 1, 1)

        for label in [uname_label, rname_label, pword_label, pword_label2]:
            label.set_halign(Gtk.Align.START)

    def clear_form(self):
        items = [
            self.uname_field,
            self.rname_field,
            self.pword_field,
            self.pword_field2
        ]
        for entry in items:
            entry.set_text("")
        for check in [self.adminuser]:
            check.set_active(False)
        self.adminuser.set_sensitive(True)

    def add_user(self, w=None):
        user = User(self.uname_field.get_text(),
                    self.rname_field.get_text(),
                    self.pword_field.get_text(),
                    False,
                    self.adminuser.get_active())
        self.owner.add_new_user(user)
        self.owner.show_main()


class InstallerUsersPage(BasePage):
    """ User management. """

    info = None

    def __init__(self):
        BasePage.__init__(self)

    def get_title(self):
        return "Who will use this device?"

    def get_name(self):
        return "users"

    def get_icon_name(self):
        return "system-users-symbolic"

    def prepare(self, info):
        self.info = info
        self.info.owner.set_can_next(True)
