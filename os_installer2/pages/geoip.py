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
from gi.repository import GLib, Gtk
import urllib2
import threading
import re
import pygeoip

IP_CHECK = "https://solus-project.com/geoip.php"
TIMEOUT = 10


class InstallerGeoipPage(BasePage):
    """ Geoip lookup. """

    info = None
    tried_find = False
    spinner = None
    dlabel = None

    def __init__(self):
        BasePage.__init__(self)

        hbox = Gtk.HBox(0)
        self.pack_start(hbox, True, True, 0)
        hbox.set_margin_top(20)
        hbox.set_border_width(40)

        self.spinner = Gtk.Spinner()
        hbox.pack_start(self.spinner, False, False, 10)

        self.dlabel = Gtk.Label("<big>Finding your location" + u"…" + "</big>")
        self.dlabel.set_use_markup(True)
        self.dlabel.set_halign(Gtk.Align.START)
        hbox.pack_start(self.dlabel, False, False, 10)

        hbox.set_halign(Gtk.Align.CENTER)

    def get_title(self):
        return "Looking for your location" + u"…"

    def get_name(self):
        return "geoip-lookup"

    def get_icon_name(self):
        return "find-location-symbolic"

    def prepare(self, info):
        self.info = info
        if not self.info.enable_geoip:
            self.info.owner.skip_page()
            return
        if self.info.cached_timezone:
            self.info.owner.skip_page()
            return
        if self.tried_find:
            return

        # Start our geoip thread
        self.schedule_lookup()

    def schedule_lookup(self):
        self.tried_find = True
        self.info.owner.set_can_next(False)
        self.info.owner.set_can_previous(False)
        self.spinner.start()
        GLib.idle_add(self.begin_thread)

    def begin_thread(self):
        t = threading.Thread(target=self.perform_lookup)
        t.start()
        return False

    def end_thread(self):
        if self.info.cached_location:
            l = self.info.cached_location
            t = self.info.cached_timezone
            c = "<b>{}</b> {}".format(l, t)
            self.dlabel.set_markup("<big>Found location: {}</big>".format(c))
        else:
            self.dlabel.set_markup("<big>Unable to find location</big>")
        self.info.owner.set_can_next(True)
        self.info.owner.set_can_previous(True)
        self.spinner.stop()
        return False

    def get_ip_address(self):
        """ Get our external IP address for this machine """
        try:
            o = urllib2.urlopen(IP_CHECK, None, TIMEOUT)
            contents = o.read()
            regex = r'Address: (\d+\.\d+\.\d+\.\d+)'
            reg = re.compile(regex)
            return reg.search(contents).group(1)
        except Exception as e:
            print(e)
        return None

    def perform_lookup(self):
        """ Perform the actual lookup """
        ip = self.get_ip_address()
        if not ip:
            # Consider getting something useful here...
            GLib.idle_add(self.end_thread)
            return

        gi = pygeoip.GeoIP("/usr/share/GeoIP/City.dat")
        country = gi.country_code_by_addr(ip)
        timezone = gi.time_zone_by_addr(ip)
        self.info.cached_location = country
        self.info.cached_timezone = timezone
        # Return to thread main
        GLib.idle_add(self.end_thread)
