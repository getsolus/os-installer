#!/usr/bin/env python2.7
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
from gi.repository import Gtk, GObject
from basepage import BasePage
import os

from os_installer.resources import RESOURCE_DIR


class LanguageItem(Gtk.HBox):

    def __init__(self, language, country, locale, language_code, country_code):
        Gtk.HBox.__init__(self)
        flag_path = RESOURCE_DIR + '/flags/48/' + country_code + '.png'
        generic_path = RESOURCE_DIR + "/flags/48/generic.png"
        self.image = Gtk.Image()
        self.image.set_padding(5, 5)
        if os.path.exists(flag_path):
            self.image.set_from_file(flag_path)
        else:
            self.image.set_from_file(generic_path)
        self.pack_start(self.image, False, False, 0)

        self.language_label = Gtk.Label()
        self.language_string = "%s (%s)" % (language, country)
        self.language_label.set_markup(self.language_string)
        self.country_code = country_code
        self.language_code = language_code
        self.pack_start(self.language_label, False, True, 0)

        self.locale = locale  # Note we need the encoding too when we hook up the installer core


class LanguagePage(BasePage):

    def __init__(self, installer):
        BasePage.__init__(self)
        # self.set_border_width(30)
        self.installer = installer

        # Nice listbox to hold our languages
        self.listbox = Gtk.ListBox()
        self.listbox.connect("row-activated", self.activated)
        scroller = Gtk.ScrolledWindow(None, None)
        scroller.add_with_viewport(self.listbox)
        scroller.set_margin_top(50)
        scroller.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        self.pack_start(scroller, True, True, 0)

        self._load_lists()

        self.installer.can_go_back(False)
        self.installer.can_go_forward(False)
        self.locale = None
        self.locale_item = None

        self.prepped = False

    def prepare(self):
        GObject.idle_add(self.set_once)
        self.installer.can_go_back(False)
        self.installer.can_go_forward(self.locale is not None)

    def set_once(self):
        if self.prepped:
            return
        self.prepped = True
        known_country = None
        if "country" in self.installer.suggestions:
            known_country = self.installer.suggestions["country"]

        selected = None
        for child in self.listbox.get_children():
            item = child.get_children()[0]
            if known_country is not None and known_country.lower() == item.country_code:
                if selected is None:
                    selected = child
                    self.locale = item.locale
                    self.locale_item = item
                elif item.language_code == "en":
                    # prefer english
                    selected = child
                    self.locale = item.locale
                    self.locale_item = item
                    break

        if selected is not None:
            self.listbox.select_row(selected)
            self.installer.can_go_forward(True)
            selected.grab_focus()

    def activated(self, box, row):
        item = row.get_children()[0]
        self.locale = item.locale
        self.locale_item = item
        self.installer.can_go_forward(True)

    def _load_lists(self):
        # Load countries into memory
        countries = {}
        file = open(os.path.join(RESOURCE_DIR, 'countries'), "r")
        for line in file:
            line = line.strip()
            split = line.split("=")
            if len(split) == 2:
                countries[split[0]] = split[1]
        file.close()

        # Load languages into memory
        languages = {}
        file = open(os.path.join(RESOURCE_DIR, 'languages'), "r")
        for line in file:
            line = line.strip()
            split = line.split("=")
            if len(split) == 2:
                languages[split[0]] = split[1]
        file.close()

        path = os.path.join(RESOURCE_DIR, 'locales')
        locales = open(path, "r")
        cur_index = -1  # find the locale :P
        set_index = None

        appends = []

        for line in locales:
            cur_index += 1
            if "UTF-8" in line:
                locale_code = line.replace("UTF-8", "")
                locale_code = locale_code.replace(".", "")
                locale_code = locale_code.strip()
                if "_" in locale_code:
                    split = locale_code.split("_")
                    if len(split) == 2:
                        language_code = split[0]
                        if language_code in languages:
                            language = languages[language_code]
                        else:
                            language = language_code

                        country_code = split[1].lower()
                        if country_code in countries:
                            country = countries[country_code]
                        else:
                            country = country_code

                        item = LanguageItem(
                            language, country, locale_code, language_code, country_code)
                        appends.append(item)

        appends.sort(key=lambda x: x.language_string.lower())
        index = 0
        selected = None
        for item in appends:
            self.listbox.add(item)

    def get_title(self):
        return _("Choose a language")

    def get_name(self):
        return "language"

    def get_icon_name(self):
        return "preferences-desktop-locale-symbolic"

    def get_primary_answer(self):
        return self.locale_item.language_string

    def seed(self, setup):
        setup.language = self.locale_item.locale
