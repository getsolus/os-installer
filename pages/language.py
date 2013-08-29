#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  changes_page.py - Whats new, etc
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
import os

class LanguageItem(Gtk.HBox):

    def __init__(self, language, country, locale, country_code, resource_dir):
        Gtk.HBox.__init__(self)
        flag_path = resource_dir + '/flags/48/' + country_code + '.png'
        generic_path = resource_dir + "/flags/48/generic.png"
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
        self.pack_start(self.language_label, False, True, 0)
        

        
class LanguagePage(BasePage):

    def __init__(self):
        BasePage.__init__(self)
        #self.set_border_width(30)
        
        # Nice listbox to hold our languages
        self.listbox = Gtk.ListBox()
        scroller = Gtk.ScrolledWindow(None, None)
        scroller.add(self.listbox)
        scroller.set_margin_top(50)
        scroller.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        self.pack_start(scroller, True, True, 0)
        
        # TEMPORARY
        self.resource_dir = "./data"
        self._load_lists()
        # Add content

    def _load_lists(self):
        #Load countries into memory
        countries = {}
        file = open(os.path.join(self.resource_dir, 'countries'), "r")
        for line in file:
            line = line.strip()
            split = line.split("=")
            if len(split) == 2:
                countries[split[0]] = split[1]
        file.close()

        #Load languages into memory
        languages = {}
        file = open(os.path.join(self.resource_dir, 'languages'), "r")
        for line in file:
            line = line.strip()
            split = line.split("=")
            if len(split) == 2:
                languages[split[0]] = split[1]
        file.close()

        path = os.path.join(self.resource_dir, 'locales')
        locales = open(path, "r")
        cur_index = -1 # find the locale :P
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

                        item = LanguageItem(language, country, locale_code, country_code, self.resource_dir)
                        appends.append(item)
                        '''iter = model.append()
                        model.set_value(iter, 0, language_label)
                        model.set_value(iter, 1, locale_code)
                        flag_path = self.resource_dir + '/flags/16/' + country_code + '.png'
                        if os.path.exists(flag_path):
                            model.set_value(iter, 2, gtk.gdk.pixbuf_new_from_file(flag_path))
                        else:
                            flag_path = self.resource_dir + '/flags/16/generic.png'
                            model.set_value(iter, 2, gtk.gdk.pixbuf_new_from_file(flag_path))'''
                        # If it's matching our country code, that's our language right there.. 
                        '''if ((cur_country_code is not None) and (cur_country_code.lower() == country_code)):                            
                            if (set_index is None):
                                set_index = iter                                
                            else:
                                # If we find more than one language for a particular country, one of them being English, go for English by default.
                                if (language_code == "en"):
                                    set_index = iter                 
                                # Guesswork... handy for countries which have their own language (fr_FR, de_DE, es_ES.. etc. )
                                elif (country_code == language_code):
                                    set_index = iter
                                    
                        # as a plan B... use the locale (USA)
                        if((set_index is None) and (locale_code == cur_lang)):
                            set_index = iter
                            #print "Set via locale: " + cur_lang'''

        appends.sort(key=lambda x: x.language_string.lower())
        for item in appends:
            self.listbox.add(item)
            #appends.remove(item)

    def get_title(self):
        return _("Choose a language")

    def get_name(self):
        return "language"

    def get_icon_name(self):
        return "preferences-desktop-locale-symbolic"
