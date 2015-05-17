#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  users.py - User management
#  
#  Copyright 2013 Ikey Doherty <ikey@solusos.com>
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
import gi.repository
from gi.repository import Gtk
from basepage import BasePage
import re
from os_installer.installer import User

LABEL_COLUMN = 0
DATA_COLUMN = 1
UNAME_REGEX = "^[a-z_][a-z0-9_-]*[$]?$"
PASSWORD_LENGTH = 6


def justify_label(lab):
    lab.set_justify(Gtk.Justification.RIGHT)
    lab.set_alignment(1.0, 0.5)

def justify_label2(lab):
    lab.set_justify(Gtk.Justification.LEFT)
    lab.set_alignment(0.0, 0.5)


class UserPanel(Gtk.VBox):
    '''
    Userpanel. Represents a user. Eventually will have Face support
    '''
    
    def __init__(self, user):
        Gtk.VBox.__init__(self)
        
        self.user = user

        label = Gtk.Label("<big>%s</big> - %s" % (self.user.realname, self.user.username))
        label.set_use_markup(True)
        label_details = Gtk.Label("")
        details = ""
        if self.user.autologin:
            details += "     - %s" % _("will be automatically logged into the computer")
        else:
            details += "     - %s" % _("will use a password to log into the computer")
        if self.user.admin:
            details += "\n     - %s" % _("will have administrative capabilities")
        else:
            details += "\n     - %s" % _("will be an ordinary user")

        label_details.set_markup(details)
        justify_label2(label)
        justify_label2(label_details)
        self.pack_start(label, True, True, 4)
        self.pack_start(label_details, False, False, 0)
        
class NewUserPage(Gtk.Grid):

    def validator(self, entry):
        if entry == self.uname_field:
            # Perform username validation
            if self.username_regex.match(entry.get_text()):
                self.uname_field.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "emblem-ok-symbolic")
                self.update_score(self.uname_field, True)
            else:
                self.uname_field.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, None)
                self.update_score(self.uname_field, False)
        elif entry == self.rname_field:
            # Only care that it's .. what?
            if len(self.rname_field.get_text()) > 1:
                self.rname_field.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "emblem-ok-symbolic")
                self.update_score(self.rname_field, True)
            else:
                self.rname_field.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, None)
                self.update_score(self.rname_field, False)
        else:
            # Handle the two password fields together
            pass1 = self.pword_field.get_text()
            pass2 = self.pword_field2.get_text()

            if len(pass1) >= PASSWORD_LENGTH:
                self.pword_field.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "emblem-ok-symbolic")
                self.update_score(self.pword_field, True)
            else:
                self.pword_field.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, None)
                self.update_score(self.pword_field, False)
                
            if len(pass1) >= PASSWORD_LENGTH and pass1 == pass2:
                self.pword_field2.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "emblem-ok-symbolic")
                self.update_score(self.pword_field2, True)
            else:
                self.pword_field2.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, None)
                self.update_score(self.pword_field2, False)

    def update_score(self, widget, score):
        if not widget in self.scores:
            self.scores[widget] = score
        else:
            self.scores[widget] = score

        total_score = len( [i for i in self.scores.values() if i])
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

        self.username_regex = re.compile(UNAME_REGEX)

        row = 0
        uname_label = Gtk.Label(_("Username:"))
        self.uname_field = Gtk.Entry()
        self.uname_field.set_hexpand(True)
        self.uname_field.connect("changed", self.validator)
        self.attach(uname_label, LABEL_COLUMN, row, 1, 1)
        self.attach(self.uname_field, DATA_COLUMN, row, 1, 1)

        row += 1
        rname_label = Gtk.Label(_("Real name:"))
        self.rname_field = Gtk.Entry()
        self.rname_field.connect("changed", self.validator)
        self.attach(rname_label, LABEL_COLUMN, row, 1, 1)
        self.attach(self.rname_field, DATA_COLUMN, row, 1, 1)

        row += 1
        pword_label = Gtk.Label(_("Password:"))
        self.pword_field = Gtk.Entry()
        self.pword_field.set_visibility(False)
        self.pword_field.connect("changed", self.validator)
        self.attach(pword_label, LABEL_COLUMN, row, 1, 1)
        self.attach(self.pword_field, DATA_COLUMN, row, 1, 1)

        row += 1
        pword_label2 = Gtk.Label(_("Confirm password:"))
        self.pword_field2 = Gtk.Entry()
        self.pword_field2.connect("changed", self.validator)
        self.pword_field2.set_visibility(False)
        self.attach(pword_label2, LABEL_COLUMN, row, 1, 1)
        self.attach(self.pword_field2, DATA_COLUMN, row, 1, 1)

        #row += 1
        # Now we have an automatic login field
        #self.autologin = Gtk.CheckButton(_("Log this user into the computer automatically"))
        #self.attach(self.autologin, DATA_COLUMN, row, 1, 1)

        row += 1
        # And now an administrative user check
        self.adminuser = Gtk.CheckButton(_("This user should have administrative capabilities"))
        self.attach(self.adminuser, DATA_COLUMN, row, 1, 1)

        row += 1
        btnbox = Gtk.ButtonBox()
        btnbox.set_spacing(5)
        # Lastly the action buttons
        self.ok = Gtk.Button(_("Add now"))
        ok_image = Gtk.Image()
        ok_image.set_from_icon_name("list-add-symbolic", Gtk.IconSize.BUTTON)
        self.ok.set_image(ok_image)
        self.ok.set_sensitive(False)
        self.ok.connect("clicked", self.add_user)

        self.cancel = Gtk.Button(_("Cancel"))
        self.cancel.connect("clicked", lambda x: self.owner.show_main())
        cancel_image = Gtk.Image()
        cancel_image.set_from_icon_name("window-close-symbolic", Gtk.IconSize.BUTTON)
        self.cancel.set_image(cancel_image)

        btnbox.set_layout(Gtk.ButtonBoxStyle.START)
        btnbox.set_margin_top(10)
        btnbox.add(self.ok)
        btnbox.add(self.cancel)
        self.attach(btnbox, DATA_COLUMN, row, 1, 1)

        for label in [uname_label, rname_label, pword_label, pword_label2]:
            justify_label(label)

    def clear_form(self):
        for entry in [self.uname_field, self.rname_field, self.pword_field, self.pword_field2]:
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

class UsersPage(BasePage):

    def __init__(self, installer):
        BasePage.__init__(self)

        self.installer = installer

        self.listbox = Gtk.ListBox()
        self.listbox.connect("row-activated", self.activated)
        scroller = Gtk.ScrolledWindow(None,None)
        scroller.add(self.listbox)
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroller.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        scroller.get_style_context().set_junction_sides(Gtk.JunctionSides.BOTTOM)

        # Placeholder stuff
        placeholder = Gtk.Label("<big>\n%s</big>" % _("You haven\'t added any users yet."))
        placeholder.set_use_markup(True)
        placeholder.show()
        self.listbox.set_placeholder(placeholder)

        toolbar = Gtk.Toolbar()
        toolbar.get_style_context().add_class(Gtk.STYLE_CLASS_INLINE_TOOLBAR)
        junctions = Gtk.JunctionSides.TOP
        toolbar.get_style_context().set_junction_sides(junctions)
        
        add = Gtk.ToolButton()
        add.connect("clicked", self.add_user)
        add.set_icon_name("list-add-symbolic")
        toolbar.add(add)

        self.remove = Gtk.ToolButton()
        self.remove.set_icon_name("list-remove-symbolic")
        self.remove.set_sensitive(False)
        self.remove.connect("clicked", self.delete_user)
        toolbar.add(self.remove)

        # We use a stack here too, because dialogs are horrible.
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_UP_DOWN)
        self.pack_start(self.stack, True, True, 0)

        main_page = Gtk.VBox()
        main_page.pack_start(scroller, True, True, 0)
        main_page.pack_start(toolbar, False, False, 0)

        self.stack.add_named(main_page, "main")

        self.add_user_page = NewUserPage(self)
        self.stack.add_named(self.add_user_page, "add-user")

        self.users = []

    def activated(self, box, row):
        if row is None:
            self.remove.set_sensitive(False)
            return
        self.remove.set_sensitive(True)

    def delete_user(self, w=None):
        row = self.listbox.get_selected_row()
        if row is None:
            self.remove.set_sensitive(False)
            return
        user = row.get_children()[0].user
        self.users.remove(user)
        self.listbox.remove(row)
        self.remove.set_sensitive(False)

        if len(self.users) == 0:
            self.installer.can_go_forward(False)

    def add_user(self, widget):
        admins = [user for user in self.users if user.admin]
        self.stack.set_visible_child_name("add-user")
        if len(admins) == 0:
            # Force this new user to be an administrator
            self.add_user_page.adminuser.set_sensitive(False)
            self.add_user_page.adminuser.set_active(True)
        self.installer.can_go_back(False)

    def add_new_user(self, user):
        self.users.append(user)
        user_panel = UserPanel(user)
        self.listbox.add(user_panel)
        self.listbox.show_all()
        self.installer.can_go_forward(True)

    def show_main(self):
        self.stack.set_visible_child_name("main")
        self.installer.can_go_back(True)
        self.add_user_page.clear_form()

    def prepare(self):
        self.installer.can_go_back(True)
        self.installer.can_go_forward(len(self.users) > 0)
        self.stack.set_visible_child_name("main")
        self.show_all()
        self.add_user_page.clear_form()

    def get_title(self):
        return _("Add users to the system")

    def get_name(self):
        return "users"

    def seed(self, setup):
        setup.users = self.users
        
    def get_icon_name(self):
        return "system-users-symbolic"

    def get_primary_answer(self):
        users = [user.username for user in self.users]
        return ", ".join(users)
