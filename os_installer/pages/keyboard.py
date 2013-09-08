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
from gi.repository import Gtk, GObject
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

        self.description = description
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

        self.description = description
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

        self.listbox_models.connect("row-activated", self.activate)

        self.listbox_layouts = Gtk.ListBox()
        scroller2 = Gtk.ScrolledWindow(None, None)
        scroller2.add(self.listbox_layouts)
        scroller2.set_shadow_type(Gtk.ShadowType.ETCHED_IN)

        self.listbox_layouts.connect("row-activated", self.activate)
        
        scroller_holder.pack_start(scroller, True, True, 0)
        scroller_holder.set_margin_top(20)
        scroller_holder.set_margin_bottom(20)

        # Stack to hold panes
        self.stack = Gtk.Stack()
        self.stack.add_named(scroller_holder, "models")
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_UP_DOWN)

        self.pack_start(self.stack, True, True, 0)

        # Page 2
        page2 = Gtk.VBox()
        page2.add(scroller2)
        self.stack.add_named(page2, "layouts")
        
        # To test keyboard layouts
        self.test_keyboard = Gtk.Entry()
        self.test_keyboard.set_placeholder_text(_("Type here to test your keyboard layout"))
        self.pack_end(self.test_keyboard, False, False, 0)

        self.wanted_model = None
        self.wanted_layout = None
        self._shown_model = False
        self._shown_layout = False
        
        # Do some loading
        self.build_kb_lists()

    def activate(self, box, row):
        child = row.get_children()[0]
        # Do something with that ^

        if isinstance(child, KeyboardPanel):
            self.wanted_model = child.model
        else:
            self.wanted_layout = child.layout

        if box == self.listbox_models:
            self.stack.set_visible_child_name("layouts")
            GObject.idle_add(self._set_once, True)
        else:
            self.stack.set_visible_child_name("models")

    def _set_once(self, layouts=False):
        if not layouts:
            if self._shown_model:
                return
            for row in self.listbox_models:
                child = row.get_children()[0]
                if child.model == self.keyboard_geom:
                    self.listbox_models.select_row(row)
                    self.wanted_model = child.model
                    break
            self._shown_model = True
        else:
            if self._shown_layout:
                return
            for row in self.listbox_layouts:
                child = row.get_children()[0]
                if child.layout == self.keyboard_layout:
                    self.listbox_layouts.select_row(row)
                    self.wanted_layout = child.layout
                    break
            self._shown_layout = True
                
    def prepare(self):
        GObject.idle_add(self._set_once)
        self.installer.can_go_back(True)
        self.installer.can_go_forward(True)

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
                self.keyboard_geom = substr
        p.poll()

        xml_file = '/usr/share/X11/xkb/rules/xorg.xml'      
        dom = parse(xml_file)

        # if we find the users keyboard info we can set it in the list
        set_keyboard_model = None
        set_keyboard_layout = None
        set_keyboard_variant = None

        # grab the root element
        root = dom.getElementsByTagName('xkbConfigRegistry')[0]
        # build the list of models

        _models = list()
        _layouts = list()
        root_models = root.getElementsByTagName('modelList')[0]
        for element in root_models.getElementsByTagName('model'):
            conf = element.getElementsByTagName('configItem')[0]
            name = conf.getElementsByTagName('name')[0]
            desc = conf.getElementsByTagName('description')[0]

            # Add to known items
            keyboard_panel = KeyboardPanel(self.getText(desc.childNodes), self.getText(name.childNodes))
            _models.append(keyboard_panel)

        # Sort the models
        _models.sort(key=lambda x: x.description.lower())
        for item in _models:
            self.listbox_models.add(item)

        root_layouts = root.getElementsByTagName('layoutList')[0]
        for element in root_layouts.getElementsByTagName('layout'):
            conf = element.getElementsByTagName('configItem')[0]
            name = conf.getElementsByTagName('name')[0]
            desc = conf.getElementsByTagName('description')[0]
            description = self.getText(desc.childNodes)
            name = self.getText(name.childNodes)
            layout_panel = KeyboardVariantPanel(description, name)
            _layouts.append(layout_panel)

        _layouts.sort(key=lambda x: x.description.lower())
        for item in _layouts:
            self.listbox_layouts.add(item)

    def getText(self, nodelist):
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)

    def get_title(self):
        return _("Choose a keyboard layout")

    def seed(self, setup):
        setup.keyboard_model = self.wanted_model
        setup.keyboard_layout = self.wanted_layout
        
    def get_name(self):
        return "keyboard"

    def get_icon_name(self):
        return "input-keyboard-symbolic"

    def get_primary_answer(self):
        return "%s - %s" % (self.wanted_model, self.wanted_layout)
