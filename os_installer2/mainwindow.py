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
from .pages.welcome import InstallerWelcomePage
from .pages.language import InstallerLanguagePage
from .pages.location import InstallerLocationPage
from .pages.keyboard import InstallerKeyboardPage
from . import join_resource_path as jrp
import sys


class MainWindow(Gtk.ApplicationWindow):

    stack = None
    installer_stack = None
    installer_page = None
    application = None
    prev_button = None
    next_button = None

    pages = list()
    page_index = 0

    def __init__(self, app):
        Gtk.ApplicationWindow.__init__(self, application=app)
        self.application = app

        headerbar = Gtk.HeaderBar()
        headerbar.set_show_close_button(True)
        self.set_titlebar(headerbar)
        try:
            self.set_icon_from_file(jrp("install-solus-192-arc-style.svg"))
        except:
            pass

        self.set_title("Installer")

        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_default_size(800, 600)

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
        self.prev_button.set_property("margin-start", 4)
        self.next_button.set_property("margin-start", 4)

        # Hook up actions
        self.prev_button.connect("clicked", lambda x: self.prev_page())
        self.next_button.connect("clicked", lambda x: self.next_page())
        # Load other pages here into installer_stack
        try:
            self.add_installer_page(InstallerLanguagePage())
            self.add_installer_page(InstallerLocationPage())
            self.add_installer_page(InstallerKeyboardPage())
        except Exception as e:
            print("Fatal error during startup: %s" % e)
            sys.exit(1)

        self.update_current_page()
        self.show_all()

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
        index = self.page_index + 1
        if index >= len(self.pages):
            return
        print("Moving to page %s" % index)
        self.page_index = index
        self.update_current_page()

    def prev_page(self):
        """ Move to previous page """
        index = self.page_index - 1
        if index < 0:
            return
        self.page_index = index
        self.update_current_page()

    def update_current_page(self):
        page = self.pages[self.page_index]
        # TODO: Re-seed
        self.installer_stack.set_visible_child_name(page.get_name())
