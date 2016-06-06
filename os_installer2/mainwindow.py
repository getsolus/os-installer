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
from gi.repository import Gtk, GLib, Gdk
from .diskman import DiskManager
from .permissions import PermissionsManager
from .pages.welcome import InstallerWelcomePage
from .pages.language import InstallerLanguagePage
from .pages.location import InstallerLocationPage
from .pages.geoip import InstallerGeoipPage
from .pages.keyboard import InstallerKeyboardPage
from .pages.timezone import InstallerTimezonePage
from .pages.disk_location import InstallerDiskLocationPage
from .pages.partitioning import InstallerPartitioningPage
from .pages.system import InstallerSystemPage
from .pages.users import InstallerUsersPage
from .pages.summary import InstallerSummaryPage
from .pages.progress import InstallerProgressPage
from . import join_resource_path as jrp
import sys
import threading


class InstallInfo:
    """ For tracking purposes between pages """

    # Chosen locale
    locale = None
    locale_sz = None

    # Chosen keyboard
    keyboard = None
    keyboard_sz = None

    # Main Window reference
    owner = None

    # Timezone for the system
    timezone = None
    timezone_c = None

    # The chosen disk strategy
    strategy = None

    # Whether to enable geoip lookups
    enable_geoip = False
    cached_location = None
    cached_timezone = None

    # system hostname
    hostname = None

    # Windows was detected
    windows_present = False
    system_utc = False

    users = None

    # Disk prober
    prober = None


class MainWindow(Gtk.ApplicationWindow):

    stack = None
    installer_stack = None
    installer_page = None
    application = None
    prev_button = None
    next_button = None

    pages = list()
    page_index = 0

    info = None

    disk_manager = None
    perms = None

    # Skip direction
    skip_forward = False

    can_quit = True
    is_final_step = False

    def quit_handler(self, w, udata=None):
        """ Ensure quit stuff is sane ... """
        if not self.can_quit:
            True
        return False

    def __init__(self, app):
        Gtk.ApplicationWindow.__init__(self, application=app)
        self.application = app
        try:
            self.set_icon_from_file(jrp("install-solus-192-arc-style.svg"))
        except:
            pass

        self.set_title("Installer")
        self.connect("delete-event", self.quit_handler)

        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_default_size(768, 500)

        # Main view
        self.stack = Gtk.Stack()
        ltr = Gtk.StackTransitionType.SLIDE_LEFT_RIGHT
        self.stack.set_transition_type(ltr)
        self.add(self.stack)

        # Main "install" page
        self.installer_page = Gtk.VBox(0)
        self.installer_stack = Gtk.Stack()
        self.installer_page.pack_start(self.installer_stack, True, True, 0)

        self.stack.add_named(InstallerWelcomePage(self), "welcome")
        self.installer_stack.set_transition_type(ltr)
        self.stack.add_named(self.installer_page, "install")

        # nav buttons
        bbox = Gtk.ButtonBox.new(Gtk.Orientation.HORIZONTAL)
        bbox.set_layout(Gtk.ButtonBoxStyle.SPREAD)
        bbox.set_halign(Gtk.Align.END)
        self.installer_page.pack_end(bbox, False, 0, 0)
        self.prev_button = Gtk.Button.new_with_label("Previous")
        self.next_button = Gtk.Button.new_with_label("Next")
        bbox.add(self.prev_button)
        bbox.add(self.next_button)
        bbox.set_margin_bottom(20)
        bbox.set_margin_end(30)
        bbox.set_margin_top(20)
        self.prev_button.set_property("margin-start", 4)
        self.next_button.set_property("margin-start", 4)

        self.info = InstallInfo()
        self.info.owner = self

        # Hook up actions
        self.prev_button.connect("clicked", lambda x: self.prev_page())
        self.next_button.connect("clicked", lambda x: self.next_page())
        # Load other pages here into installer_stack
        try:
            self.add_installer_page(InstallerLanguagePage())
            self.add_installer_page(InstallerLocationPage())
            self.add_installer_page(InstallerGeoipPage())
            self.add_installer_page(InstallerKeyboardPage())
            self.add_installer_page(InstallerTimezonePage())
            self.add_installer_page(InstallerDiskLocationPage())
            self.add_installer_page(InstallerPartitioningPage())
            self.add_installer_page(InstallerSystemPage())
            self.add_installer_page(InstallerUsersPage())
            self.add_installer_page(InstallerSummaryPage())
            self.add_installer_page(InstallerProgressPage())
        except Exception as e:
            print("Fatal error during startup: %s" % e)
            sys.exit(1)

        # Shared helpers
        self.perms = PermissionsManager()
        self.disk_manager = DiskManager()

        self.update_current_page()
        self.show_all()

        GLib.idle_add(self.start_threads)

    def start_threads(self):
        self.set_can_next(False)
        start_thr = threading.Thread(target=self.perform_inits)
        start_thr.daemon = True
        start_thr.start()
        return False

    def perform_inits(self):
        """ Force expensive children to init outside main thread """
        for page in self.pages:
            try:
                page.do_expensive_init()
            except Exception as e:
                print("Fatal exception initialising: %s" % e)

        # Allow next again
        Gdk.threads_enter()
        self.set_can_next(True)
        Gdk.threads_leave()

    def phase_install(self):
        self.stack.set_visible_child_name("install")

    def phase_live(self):
        """ Consider switching to another view showing how to restart the
            installer ? """
        self.application.quit()

    def add_installer_page(self, page):
        """ Work a page into the set """
        self.installer_stack.add_named(page, page.get_name())
        self.pages.append(page)

    def next_page(self):
        """ Move to next page """
        if self.is_final_step:
            msg = "Installation will make changes to your disks, and could " \
                  "result in data loss.\nDo you wish to install?"
            d = Gtk.MessageDialog(parent=self, flags=Gtk.DialogFlags.MODAL,
                                  type=Gtk.MessageType.WARNING,
                                  buttons=Gtk.ButtonsType.OK_CANCEL,
                                  message_format=msg)

            r = d.run()
            d.destroy()
            if r != Gtk.ResponseType.OK:
                return

        self.skip_forward = True
        index = self.page_index + 1
        if index >= len(self.pages):
            return
        page = self.pages[index]
        if page.is_hidden():
            index += 1
        self.page_index = index
        self.update_current_page()

    def prev_page(self):
        self.skip_forward = False
        """ Move to previous page """
        index = self.page_index - 1
        if index < 0:
            return
        page = self.pages[index]
        if page.is_hidden():
            index -= 1
        self.page_index = index
        self.update_current_page()

    def update_current_page(self):
        page = self.pages[self.page_index]
        self.set_final_step(False)

        if self.page_index == len(self.pages) - 1:
            self.set_can_next(False)
        else:
            # TODO: Have pages check next-ness
            self.set_can_next(True)
        if self.page_index == 0:
            self.set_can_previous(False)
        else:
            self.set_can_previous(True)
        page.prepare(self.info)
        self.installer_stack.set_visible_child_name(page.get_name())

    def set_can_previous(self, can_prev):
        self.prev_button.set_sensitive(can_prev)

    def set_can_next(self, can_next):
        self.next_button.set_sensitive(can_next)

    def set_final_step(self, final):
        """ Mark this as the final step, should also
            add a prompt on selection """
        if final:
            self.next_button.set_label("Install")
        else:
            self.next_button.set_label("Next")
        self.is_final_step = final

    def set_can_quit(self, can_quit):
        """ Override quit handling """
        self.can_quit = can_quit
        if not self.can_quit:
            self.prev_button.hide()
            self.next_button.hide()
            # self.set_deletable(False)
        else:
            self.prev_button.show_all()
            self.next_button.show_all()
            # self.set_deletable(True)

    def get_disk_manager(self):
        """ Return our disk manager object """
        return self.disk_manager

    def get_perms_manager(self):
        """ Return permission manager """
        return self.perms

    def skip_page(self):
        GLib.idle_add(self._skip_page)

    def _skip_page(self):
        """ Allow pages to request skipping to next page """
        if self.skip_forward:
            self.next_page()
        else:
            self.prev_page()
        return False
