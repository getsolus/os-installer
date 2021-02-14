# coding=utf-8
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

from gi.repository import Gio, Gtk

from .mainwindow import MainWindow

APP_ID = "com.solus_project.Installer"


class InstallerApplication(Gtk.Application):
    app_window = None

    def __init__(self):
        Gtk.Application.__init__(self,
                                 application_id=APP_ID,
                                 flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        if self.app_window is None:
            self.app_window = MainWindow(self)
        self.app_window.present()
