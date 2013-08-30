#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  keyboard.py - Keyboard selection
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

import xml.dom.minidom
from xml.dom.minidom import parse
import subprocess

class KeyboardPanel(Gtk.Bin):
    ''' Represents each keyboard model '''
    def __init__(self, description, name):
        Gtk.Bin.__init__(self)

        line1 = description.strip()
        lab1 = Gtk.Label("<big>%s</big>" % description)
        lab1.set_use_markup(True)
        lab1.set_alignment(0.1, 0.5)
        lab1.set_justify(Gtk.Justification.LEFT)

        container = Gtk.HBox()
        container.pack_start(lab1, False, True, 0)
        self.add(container)
        self.set_border_width(3)

        self.model = name

class KeyboardVariantPanel(Gtk.Bin):
    ''' Represents each keyboard layout '''
    def __init__(self, description, name):
        Gtk.Bin.__init__(self)

        line1 = description.strip()
        lab1 = Gtk.Label("<big>%s</big>" % description)
        lab1.set_use_markup(True)
        lab1.set_alignment(0.1, 0.5)
        lab1.set_justify(Gtk.Justification.LEFT)

        container = Gtk.HBox()
        container.pack_start(lab1, False, True, 0)
        self.add(container)
        self.set_border_width(3)

        self.layout = name
    
class KeyboardPage(BasePage):

    def __init__(self, installer):
        BasePage.__init__(self)
        

        self.installer = installer

        scroller_holder = Gtk.HBox(10, 10)
        
        self.listbox_models = Gtk.ListBox()
        scroller = Gtk.ScrolledWindow(None, None)
        scroller.add(self.listbox_models)
        scroller.set_shadow_type(Gtk.ShadowType.ETCHED_IN)


        self.listbox_layouts = Gtk.ListBox()
        scroller2 = Gtk.ScrolledWindow(None, None)
        scroller2.add(self.listbox_layouts)
        scroller2.set_shadow_type(Gtk.ShadowType.ETCHED_IN)

        scroller_holder.pack_start(scroller, True, True, 0)
        scroller_holder.pack_start(scroller2, True, True, 0)
        scroller_holder.set_margin_top(20)
        scroller_holder.set_margin_bottom(20)
        self.pack_start(scroller_holder, True, True, 0)

        # To test keyboard layouts
        self.test_keyboard = Gtk.Entry()
        self.test_keyboard.set_placeholder_text(_("Type here to test your keyboard layout"))
        self.pack_end(self.test_keyboard, False, False, 0)
       
        
        # Do some loady loady
        self.build_kb_lists()
        self.build_kb_variant_lists()

    def prepare(self):
        self.installer.can_go_back(True)
        self.installer.can_go_forward(False)

    def build_kb_lists(self):
        ''' Do some xml kung-fu and load the keyboard stuffs '''

        # firstly we'll determine the layouts in use
        p = subprocess.Popen("setxkbmap -print",shell=True,stdout=subprocess.PIPE)
        for line in p.stdout:
            # strip it
            line = line.rstrip("\r\n")
            line = line.replace("{","")
            line = line.replace("}","")
            line = line.replace(";","")
            if("xkb_symbols" in line):
                # decipher the layout in use
                section = line.split("\"")[1] # split by the " mark
                self.keyboard_layout = section.split("+")[1]
            if("xkb_geometry" in line):
                first_bracket = line.index("(") +1
                substr = line[first_bracket:]
                last_bracket = substr.index(")")
                substr = substr[0:last_bracket]
                keyboard_geom = substr
        p.poll()

        xml_file = '/usr/share/X11/xkb/rules/xorg.xml'
        model_models = Gtk.ListStore(str,str)
        model_models.set_sort_column_id(0, Gtk.SortType.ASCENDING)

        model_layouts = Gtk.ListStore(str,str)
        model_layouts.set_sort_column_id(0, Gtk.SortType.ASCENDING)      
        dom = parse(xml_file)

        # if we find the users keyboard info we can set it in the list
        set_keyboard_model = None
        set_keyboard_layout = None
        set_keyboard_variant = None

        # grab the root element
        root = dom.getElementsByTagName('xkbConfigRegistry')[0]
        # build the list of models
        selected_index = index = -1
        root_models = root.getElementsByTagName('modelList')[0]
        for element in root_models.getElementsByTagName('model'):
            conf = element.getElementsByTagName('configItem')[0]
            name = conf.getElementsByTagName('name')[0]
            desc = conf.getElementsByTagName('description')[0]
            #vendor = conf.getElementsByTagName('vendor')[0] # presently unused..
            iter_model = model_models.append([self.getText(desc.childNodes), self.getText(name.childNodes)])
            index += 1
            item = self.getText(name.childNodes)
            if(item == keyboard_geom):
                set_keyboard_model = iter_model
                selected_index = index

            # Add to known items
            keyboard_panel = KeyboardPanel(self.getText(desc.childNodes), self.getText(name.childNodes))
            self.listbox_models.add(keyboard_panel)

        row = self.listbox_models.get_row_at_index(selected_index)
        self.listbox_models.select_row(row)
            
    def build_kb_variant_lists(self):
        # firstly we'll determine the layouts in use
        p = subprocess.Popen("setxkbmap -print",shell=True,stdout=subprocess.PIPE)
        for line in p.stdout:
            # strip it
            line = line.rstrip("\r\n")
            line = line.replace("{","")
            line = line.replace("}","")
            line = line.replace(";","")
            if("xkb_symbols" in line):
                # decipher the layout in use
                section = line.split("\"")[1] # split by the " mark
                self.keyboard_layout = section.split("+")[1]
        p.poll()

        xml_file = '/usr/share/X11/xkb/rules/xorg.xml'      
        #model_variants = gtk.ListStore(str,str)
        #model_variants.set_sort_column_id(0, gtk.SORT_ASCENDING)        
        dom = parse(xml_file)

        index = -1
        # grab the root element
        root = dom.getElementsByTagName('xkbConfigRegistry')[0]
        # build the list of variants       
        root_layouts = root.getElementsByTagName('layoutList')[0]
        for layout in root_layouts.getElementsByTagName('layout'):
            conf = layout.getElementsByTagName('configItem')[0]
            layout_name = self.getText(conf.getElementsByTagName('name')[0].childNodes)            
            layout_description = self.getText(conf.getElementsByTagName('description')[0].childNodes)
                
            if (layout_name == self.keyboard_layout):
                #iter_variant = model_variants.append([layout_description, None])
                variant_panel = KeyboardVariantPanel(layout_description, None)
                self.listbox_layouts.add(variant_panel)
                variants_list = layout.getElementsByTagName('variantList')
                index += 1
                
                if len(variants_list) > 0:
                    root_variants = layout.getElementsByTagName('variantList')[0]   
                    for variant in root_variants.getElementsByTagName('variant'):                    
                        variant_conf = variant.getElementsByTagName('configItem')[0]
                        variant_name = self.getText(variant_conf.getElementsByTagName('name')[0].childNodes)
                        variant_description = "%s - %s" % (layout_description, self.getText(variant_conf.getElementsByTagName('description')[0].childNodes))
                        variant_panel = KeyboardVariantPanel(variant_description, variant_name)
                        self.listbox_layouts.add(variant_panel)
                break

        # Select it
        row = self.listbox_layouts.get_row_at_index(index)
        self.listbox_layouts.select_row(row)

    def getText(self, nodelist):
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)

    def get_title(self):
        return _("Choose a keyboard layout")

    def get_name(self):
        return "keyboard"

    def get_icon_name(self):
        return "input-keyboard-symbolic"

    def get_primary_answer(self):
        return self.locale_item.language_string
