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
from .pages.complete import InstallationCompletePage
import sys
import threading
import traceback

class FancyLabel(Gtk.Label):

    page_id = None

    def __init__(self, page):
        Gtk.Label.__init__(self)
        self.set_label(page.get_sidebar_title())
        self.page_id = page.get_name()
        self.set_halign(Gtk.Align.START)
        self.set_property("margin", 6)
        self.set_property("margin-start", 24)
        self.set_property("margin-end", 24)
        self.get_style_context().add_class("dim-label")

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

    users = None

    # Disk prober
    prober = None

    # Bootloader target
    bootloader = None
    bootloader_sz = None
    bootloader_install = False

    invalidated = False

    def __init__(self):
        self.users = list()
        self.bootloader_install = True


class MainWindow(Gtk.ApplicationWindow):

    stack = None
    installer_stack = None
    installer_page = None
    application = None
    prev_button = None
    next_button = None

    box_labels = None

    pages = list()
    page_index = 0

    info = None

    disk_manager = None
    perms = None

    # Skip direction
    skip_forward = False

    can_quit = True
    is_final_step = False

    image_step = None
    label_step = None

    def quit_handler(self, w, udata=None):
        """ Ensure quit stuff is sane ... """
        if not self.can_quit:
            True
        return False

    def __init__(self, app):
        Gtk.ApplicationWindow.__init__(self, application=app)
        self.application = app

        Gtk.Settings.get_default().set_property("gtk-application-prefer-dark-theme", False)

        self.image_step = Gtk.Image.new_from_icon_name("system-software-install", Gtk.IconSize.DIALOG)
        self.image_step.set_property("margin", 8)
        self.label_step = Gtk.Label.new("")
        self.label_step.set_property("margin", 8)

        self.set_title("Install Solus")

        self.headerbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.headerbox.get_style_context().add_class("header-box")
        self.headerbox.pack_start(self.image_step, False, False, 0)
        # self.headerbox.pack_start(self.label_step, False, False, 0)
        self.box_labels = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.box_labels.set_valign(Gtk.Align.START)
        self.box_labels.set_property("margin-bottom", 40)
        self.box_labels.set_property("margin-top", 20)
        self.headerbox.pack_start(self.box_labels, True, True, 0)

        # Vanity! TODO: Select correct icon ..
        img_vanity = Gtk.Image.new_from_icon_name("budgie-desktop-symbolic", Gtk.IconSize.LARGE_TOOLBAR)
        img_vanity.set_property("margin", 8)
        img_vanity.set_property("margin-top", 0)
        lab_vanity = Gtk.Label.new("Solus Budgie")
        lab_vanity.set_property("margin-start", 4)
        lab_vanity.set_property("margin-end", 8)
        lab_vanity.set_property("margin-bottom", 8)
        self.headerbox.pack_end(lab_vanity, False, False, 0)
        self.headerbox.pack_end(img_vanity, False, False, 0)

        self.set_icon_name("system-software-install")
        self.connect("delete-event", self.quit_handler)

        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_default_size(768, 500)

        # Main "install" page
        self.installer_page = Gtk.Box(Gtk.Orientation.VERTICAL, 0)
        self.installer_stack = Gtk.Stack()
        self.installer_page.pack_start(self.installer_stack, True, True, 0)

        self.installer_wrap = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.installer_wrap.pack_start(self.headerbox, False, False, 0)
        sep = Gtk.Separator.new(Gtk.Orientation.VERTICAL)
        self.installer_wrap.pack_start(sep, False, False, 0)
        self.installer_wrap.pack_start(self.installer_page, True, True, 0)

        ltr = Gtk.StackTransitionType.SLIDE_LEFT_RIGHT
        self.installer_stack.set_transition_type(ltr)
        self.add(self.installer_wrap)


        # nav buttons
        bbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 4)
        bbox.set_halign(Gtk.Align.END)
        self.prev_button = Gtk.Button.new_with_label("Previous")
        self.next_button = Gtk.Button.new_with_label("Next")
        bbox.pack_start(self.prev_button, False, False, 0)
        bbox.pack_start(self.next_button, False, False, 0)
        bbox.set_margin_top(10)
        bbox.set_margin_bottom(10)
        bbox.set_margin_end(10)
        self.prev_button.set_property("margin-start", 4)
        self.next_button.set_property("margin-start", 4)

        # sep before nav
        sep = Gtk.Separator.new(Gtk.Orientation.HORIZONTAL)
        sep.set_margin_top(20)
        self.installer_page.pack_end(bbox, False, 0, 0)
        self.installer_page.pack_end(sep, False, 0, 0)

        self.info = InstallInfo()
        self.info.owner = self

        self.get_style_context().add_class("installer-window")

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
            self.add_installer_page(InstallationCompletePage())
        except Exception as e:
            print("Fatal error during startup: {}".format(e))
            traceback.print_exc(file=sys.stderr)
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
        self.info.owner.get_perms_manager().down_permissions()
        """ Force expensive children to init outside main thread """
        for page in self.pages:
            try:
                page.do_expensive_init()
            except Exception as e:
                print("Fatal exception initialising: {}".format(e))


    def add_installer_page(self, page):
        """ Work a page into the set """
        self.installer_stack.add_named(page, page.get_name())
        lab = FancyLabel(page)
        self.box_labels.pack_start(lab, False, False, 0)
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

        for label in self.box_labels.get_children():
            if label.page_id == page.get_name():
                label.get_style_context().remove_class("dim-label")
            else:
                label.get_style_context().add_class("dim-label")

        self.image_step.set_from_icon_name(page.get_icon_name(),
                                           Gtk.IconSize.DIALOG)
        # self.image_step.set_pixel_size(32)
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
