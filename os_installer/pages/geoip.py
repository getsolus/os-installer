#!/bin/true
# -*- coding: utf-8 -*-
#
#  Copyright (C) 2013-2016 Ikey Doherty <ikey@solus-project.com>
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
from gi.repository import Gtk, Gdk
from .basepage import BasePage
import urllib.request
import urllib.error
import urllib.parse
import re
import pygeoip
import threading

IP_CHECK = "http://checkip.dyndns.com/"

TIMEOUT = 4


class GeoPage(BasePage):

    def __init__(self, installer):
        BasePage.__init__(self)
        self.installer = installer

        label_info = _(
            """The next few questions will relate to your location and language. In order to speed things up,
we can perform a quick check to find out where you are in the world. To opt out, just click Next.""")

        lab_w = Gtk.Label(label_info)

        self.pack_start(lab_w, False, False, 0)

        hbox = Gtk.HBox()
        self.btn = Gtk.Button("Find my location automatically")
        self.btn.connect("clicked", self.lookup)
        hbox.pack_start(self.btn, False, False, 5)

        self.stat_label = Gtk.Label("")
        hbox.pack_end(self.stat_label, False, False, 5)
        self.spinner = Gtk.Spinner()
        hbox.pack_end(self.spinner, False, False, 0)

        hbox.set_border_width(40)
        self.pack_start(hbox, False, False, 20)

    def _get_ip(self):
        try:
            o = urllib.request.urlopen(IP_CHECK, None, TIMEOUT)
            contents = o.read()
            regex = r'Address: (\d+\.\d+\.\d+\.\d+)'
            reg = re.compile(regex)
            return reg.search(contents).group(1)
        except Exception as e:
            print(e)

        return None

    def _lookup(self):
        ''' TODO: Make threaded. And useful. '''
        Gdk.threads_enter()
        self.installer.can_go_forward(False)

        self.spinner.set_visible(True)
        self.spinner.start()
        self.btn.set_sensitive(False)
        self.stat_label.set_markup(_("Resolving IP"))
        Gdk.threads_leave()

        ip = self._get_ip()
        if ip is None:
            Gdk.threads_enter()
            self.stat_label.set_markup(_("Failed to determine location"))
            self.btn.set_sensitive(True)
            self.installer.can_go_forward(True)
            self.spinner.stop()
            Gdk.threads_leave()
            return

        gi = pygeoip.GeoIP("/usr/share/GeoIP/City.dat")
        country = gi.country_code_by_addr(ip)
        timezone = gi.time_zone_by_addr(ip)

        Gdk.threads_enter()
        self.stat_label.set_markup(_("Found: %s" % timezone))
        self.spinner.stop()
        self.spinner.hide()
        self.installer.can_go_forward(True)
        Gdk.threads_leave()

        self.installer.suggestions["country"] = country
        self.installer.suggestions["timezone"] = timezone

    def lookup(self, btn=None):
        t = threading.Thread(target=self._lookup)
        t.start()

    def prepare(self):
        self.installer.can_go_back(False)
        self.installer.can_go_forward(True)
        self.spinner.set_visible(False)

    def get_title(self):
        return _("Help us find you")

    def get_name(self):
        return "geo"

    def get_icon_name(self):
        return "find-location-symbolic"

    def get_primary_answer(self):
        return "Not yet implemented"

    def is_hidden(self):
        return True
