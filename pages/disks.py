#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  disks.py - Disk chooser
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

import subprocess
import os
import commands
import parted
import string

INDEX_PARTITION_PATH=0
INDEX_PARTITION_TYPE=1
INDEX_PARTITION_DESCRIPTION=2
INDEX_PARTITION_FORMAT_AS=3
INDEX_PARTITION_MOUNT_AS=4
INDEX_PARTITION_SIZE=5
INDEX_PARTITION_FREE_SPACE=6
INDEX_PARTITION_OBJECT=7

class DiskPanel(Gtk.HBox):

    def __init__(self, name):
        Gtk.HBox.__init__(self, 0, 10)

        # Need a shiny icon
        self.image = Gtk.Image()
        self.image.set_from_icon_name("drive-harddisk-symbolic", Gtk.IconSize.DIALOG)

        self.label = Gtk.Label(name)

        self.pack_start(self.image, False, False, 0)
        self.pack_start(self.label, False, True, 0)

        self.set_name('installer-box')
        self.set_border_width(5)
        
class PartitionSetup(object):
    name = ""    
    type = ""
    format_as = None
    mount_as = None    
    partition = None
    aggregatedPartitions = []

    def __init__(self, partition):
        self.partition = partition
        self.size = partition.getSize()
        self.start = partition.geometry.start
        self.end = partition.geometry.end
        self.description = ""
        self.used_space = ""
        self.free_space = ""

        if partition.number != -1:
            self.name = partition.path            
            if partition.fileSystem is None:
                # no filesystem, check flags
                if partition.type == parted.PARTITION_SWAP:
                    self.type = ("Linux swap")
                elif partition.type == parted.PARTITION_RAID:
                    self.type = ("RAID")
                elif partition.type == parted.PARTITION_LVM:
                    self.type = ("Linux LVM")
                elif partition.type == parted.PARTITION_HPSERVICE:
                    self.type = ("HP Service")
                elif partition.type == parted.PARTITION_PALO:
                    self.type = ("PALO")
                elif partition.type == parted.PARTITION_PREP:
                    self.type = ("PReP")
                elif partition.type == parted.PARTITION_MSFT_RESERVED:
                    self.type = ("MSFT Reserved")
                elif partition.type == parted.PARTITION_EXTENDED:
                    self.type = ("Extended Partition")
                elif partition.type == parted.PARTITION_LOGICAL:
                    self.type = ("Logical Partition")
                elif partition.type == parted.PARTITION_FREESPACE:
                    self.type = ("Free Space")
                else:
                    self.type =("Unknown")
            else:
                self.type = partition.fileSystem.type
        else:
            self.type = ""
            self.name = _("unallocated")

    def add_partition(self, partition):
        self.aggregatedPartitions.append(partition)
        self.size = self.size + partition.getSize()
        self.end = partition.geometry.end
    
    def print_partition(self):
        print "Device: %s, format as: %s, mount as: %s" % (self.partition.path, self.format_as, self.mount_as)
        
class DiskPage(BasePage):

    def __init__(self, installer):
        BasePage.__init__(self)
        self.installer = installer

        # Hold our pages in a stack
        self.stack = Gtk.Stack()

        # Disk chooser page
        self.disks_page = Gtk.VBox()
        self.disks_page.set_margin_top(30)
        self.disks_page.set_border_width(20)
        self.listbox_disks = Gtk.ListBox()
        self.disks_page.pack_start(self.listbox_disks, True, True, 0)

        self.stack.add_named(self.disks_page, "disks")
        
        # Partitioning page
        self.partition_page = Gtk.VBox()
        
        self.treeview = Gtk.TreeView()
        self.scroller = Gtk.ScrolledWindow(None, None)
        self.scroller.add(self.treeview)
        #self.scroller.set_border_width(10)
        self.scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scroller.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        self.scroller.get_style_context().set_junction_sides(Gtk.JunctionSides.BOTTOM)
        self.partition_page.pack_start(self.scroller, True, True, 0)
        
        # device
        ren = Gtk.CellRendererText()
        self.column3 = Gtk.TreeViewColumn(_("Device"), ren)
        self.column3.add_attribute(ren, "markup", INDEX_PARTITION_PATH)
        self.treeview.append_column(self.column3)
        
        # Type
        ren = Gtk.CellRendererText()
        self.column4 = Gtk.TreeViewColumn(_("Type"), ren)
        self.column4.add_attribute(ren, "markup", INDEX_PARTITION_TYPE)
        self.treeview.append_column(self.column4)
        
        # description
        ren = Gtk.CellRendererText()
        self.column5 = Gtk.TreeViewColumn(_("Operating system"), ren)
        self.column5.add_attribute(ren, "markup", INDEX_PARTITION_DESCRIPTION)
        self.treeview.append_column(self.column5)
         
        # mount point
        ren = Gtk.CellRendererText()
        self.column6 = Gtk.TreeViewColumn(_("Mount point"), ren)
        self.column6.add_attribute(ren, "markup", INDEX_PARTITION_MOUNT_AS)
        self.treeview.append_column(self.column6)
        
        # format
        ren = Gtk.CellRendererText()
        self.column7 = Gtk.TreeViewColumn(_("Format?"), ren)
        self.column7.add_attribute(ren, "markup", INDEX_PARTITION_FORMAT_AS)        
        self.treeview.append_column(self.column7)
        
        # size
        ren = Gtk.CellRendererText()
        self.column8 = Gtk.TreeViewColumn(_("Size"), ren)
        self.column8.add_attribute(ren, "markup", INDEX_PARTITION_SIZE)
        self.treeview.append_column(self.column8)
        
        # Used space
        ren = Gtk.CellRendererText()
        self.column9 = Gtk.TreeViewColumn(_("Free space"), ren)
        self.column9.add_attribute(ren, "markup", INDEX_PARTITION_FREE_SPACE)
        self.treeview.append_column(self.column9)

        toolbar = Gtk.Toolbar()
        toolbar.get_style_context().add_class(Gtk.STYLE_CLASS_INLINE_TOOLBAR)
        junctions = Gtk.JunctionSides.TOP
        toolbar.get_style_context().set_junction_sides(junctions)
        
        add = Gtk.ToolButton()
        add.set_icon_name("preferences-system-symbolic")
        toolbar.add(add)

        self.partition_page.pack_start(toolbar, False, False, 0)

        self.stack.add_named(self.partition_page, "partitions")

        self.pack_start(self.stack, True, True, 0)
        
        self.target_disk = "/dev/sda"

        self.build_hdds()
        self.build_partitions()


    def build_hdds(self):
        self.disks = []
        #model = Gtk.ListStore(str, str)            
        inxi = subprocess.Popen("inxi -c0 -D", shell=True, stdout=subprocess.PIPE)      
        for line in inxi.stdout:
            line = line.rstrip("\r\n")
            if(line.startswith("Disks:")):
                line = line.replace("Disks:", "")            
            sections = line.split(":")
            for section in sections:
                section = section.strip()
                if("/dev/" in section):                    
                    elements = section.split()
                    for element in elements:
                        if "/dev/" in element: 
                            self.disks.append(element)

        index = 0
        for disk in self.disks:
            panel = DiskPanel(disk)
            self.listbox_disks.add(panel)
            row = self.listbox_disks.get_row_at_index(index)
            row.set_name('disk-row')
            row.set_margin_bottom(5)
            index += 1
            

    def build_partitions(self):        
        #self.window.set_sensitive(False)
        # "busy" cursor.
        #cursor = gtk.gdk.Cursor(gtk.gdk.WATCH)
        #self.window.window.set_cursor(cursor)        
        
        os.popen('mkdir -p /tmp/os-installer/tmpmount')
        
        try:                                                                                            
            #grub_model = gtk.ListStore(str)
            self.partitions = []
            
            model = Gtk.ListStore(str,str,str,str,str,str,str, object, bool, long, long, bool)
            model2 = Gtk.ListStore(str)
            
            swap_found = False
            
            if self.target_disk is not None:
                path =  self.target_disk # i.e. /dev/sda
                #grub_model.append([path])
                device = parted.getDevice(path)                
                try:
                    disk = parted.Disk(device)
                except Exception:
                    # Need to raise a warning..
                    pass
                partition = disk.getFirstPartition()
                last_added_partition = PartitionSetup(partition)
                partition = partition.nextPartition()
                while (partition is not None):
                    if last_added_partition.partition.number == -1 and partition.number == -1:
                        last_added_partition.add_partition(partition)
                    else:                        
                        last_added_partition = PartitionSetup(partition)
                                        
                        if "swap" in last_added_partition.type:
                            last_added_partition.type = "swap"                                                            

                        if partition.number != -1 and "swap" not in last_added_partition.type and partition.type != parted.PARTITION_EXTENDED:
                            #Umount temp folder
                            if ('/tmp/os-installer/tmpmount' in commands.getoutput('mount')):
                                os.popen('umount /tmp/os-installer/tmpmount')

                            #Mount partition if not mounted
                            if (partition.path not in commands.getoutput('mount')):                                
                                os.system("mount %s /tmp/os-installer/tmpmount" % partition.path)

                            #Identify partition's description and used space
                            if (partition.path in commands.getoutput('mount')):
                                df_lines = commands.getoutput("df 2>/dev/null | grep %s" % partition.path).split('\n')
                                for df_line in df_lines:
                                    df_elements = df_line.split()
                                    if df_elements[0] == partition.path:
                                        last_added_partition.used_space = df_elements[4]  
                                        mount_point = df_elements[5]                              
                                        if "%" in last_added_partition.used_space:
                                            used_space_pct = int(last_added_partition.used_space.replace("%", "").strip())
                                            last_added_partition.free_space = int(float(last_added_partition.size) * (float(100) - float(used_space_pct)) / float(100))
                                        if os.path.exists(os.path.join(mount_point, 'etc/issue')):
                                            last_added_partition.description = commands.getoutput("cat " + os.path.join(mount_point, 'etc/issue')).replace('\\n', '').replace('\l', '').strip()
                                        if os.path.exists(os.path.join(mount_point, 'etc/solusos-release')):
                                            last_added_partition.description = commands.getoutput("cat " + os.path.join(mount_point, 'etc/solusos-release')).strip()                              
                                        if os.path.exists(os.path.join(mount_point, 'etc/lsb-release')):
                                            last_added_partition.description = commands.getoutput("cat " + os.path.join(mount_point, 'etc/lsb-release') + " | grep DISTRIB_DESCRIPTION").replace('DISTRIB_DESCRIPTION', '').replace('=', '').replace('"', '').strip()                                    
                                        if os.path.exists(os.path.join(mount_point, 'Windows/servicing/Version')):
                                            version = commands.getoutput("ls %s" % os.path.join(mount_point, 'Windows/servicing/Version'))                                    
                                            if version.startswith("6.1"):
                                                last_added_partition.description = "Windows 7"
                                            elif version.startswith("6.0"):
                                                last_added_partition.description = "Windows Vista"
                                            elif version.startswith("5.1") or version.startswith("5.2"):
                                                last_added_partition.description = "Windows XP"
                                            elif version.startswith("5.0"):
                                                last_added_partition.description = "Windows 2000"
                                            elif version.startswith("4.90"):
                                                last_added_partition.description = "Windows Me"
                                            elif version.startswith("4.1"):
                                                last_added_partition.description = "Windows 98"
                                            elif version.startswith("4.0.1381"):
                                                last_added_partition.description = "Windows NT"
                                            elif version.startswith("4.0.950"):
                                                last_added_partition.description = "Windows 95"
                                        elif os.path.exists(os.path.join(mount_point, 'Boot/BCD')):
                                            if os.system("grep -qs \"V.i.s.t.a\" " + os.path.join(mount_point, 'Boot/BCD')) == 0:
                                                last_added_partition.description = "Windows Vista bootloader"
                                            elif os.system("grep -qs \"W.i.n.d.o.w.s. .7\" " + os.path.join(mount_point, 'Boot/BCD')) == 0:
                                                last_added_partition.description = "Windows 7 bootloader"
                                            elif os.system("grep -qs \"W.i.n.d.o.w.s. .R.e.c.o.v.e.r.y. .E.n.v.i.r.o.n.m.e.n.t\" " + os.path.join(mount_point, 'Boot/BCD')) == 0:
                                                last_added_partition.description = "Windows recovery"
                                            elif os.system("grep -qs \"W.i.n.d.o.w.s. .S.e.r.v.e.r. .2.0.0.8\" " + os.path.join(mount_point, 'Boot/BCD')) == 0:
                                                last_added_partition.description = "Windows Server 2008 bootloader"
                                            else:
                                                last_added_partition.description = "Windows bootloader"
                                        elif os.path.exists(os.path.join(mount_point, 'Windows/System32')):
                                            last_added_partition.description = "Windows"
                                        break
                            else:
                                print "Failed to mount %s" % partition.path

                            
                            #Umount temp folder
                            if ('/tmp/os-installer/tmpmount' in commands.getoutput('mount')):
                                os.popen('umount /tmp/os-installer/tmpmount')
                                
                    if last_added_partition.size > 1.0:
                        if last_added_partition.partition.type == parted.PARTITION_LOGICAL:
                            display_name = "  " + last_added_partition.name
                        else:
                            display_name = last_added_partition.name

                        iter = model.append([display_name, last_added_partition.type, last_added_partition.description, "", "", '%.0f' % round(last_added_partition.size, 0), str(last_added_partition.free_space), last_added_partition, False, last_added_partition.start, last_added_partition.end, False]);
                        if last_added_partition.partition.number == -1:                     
                            model.set_value(iter, INDEX_PARTITION_TYPE, "<span foreground='#a9a9a9'>%s</span>" % last_added_partition.type)                                    
                        elif last_added_partition.partition.type == parted.PARTITION_EXTENDED:                    
                            model.set_value(iter, INDEX_PARTITION_TYPE, "<span foreground='#a9a9a9'>%s</span>" % _("Extended"))  
                        else:                                        
                            if last_added_partition.type == "ntfs":
                                color = "#42e5ac"
                            elif last_added_partition.type == "fat32":
                                color = "#18d918"
                            elif last_added_partition.type == "ext4":
                                color = "#4b6983"
                            elif last_added_partition.type == "ext3":
                                color = "#7590ae"
                            elif last_added_partition.type in ["linux-swap", "swap"]:
                                color = "#c1665a"
                                last_added_partition.mount_as = "swap"
                                model.set_value(iter, INDEX_PARTITION_MOUNT_AS, "swap")
                            else:
                                color = "#a9a9a9"
                            model.set_value(iter, INDEX_PARTITION_TYPE, "<span foreground='%s'>%s</span>" % (color, last_added_partition.type))                                            
                            deviceSize = float(device.getSize()) * float(0.9) # Hack.. reducing the real size to 90% of what it is, to make sure our partitions fit..
                            space = int((float(partition.getSize()) / deviceSize) * float(80))                            
                            subs = {}
                            if (space >= 10):
                                subs['path'] = display_name.replace("/dev/", "")                            
                                subs['OS'] = last_added_partition.description
                            elif (space >= 5):
                                subs['path'] = display_name.replace("/dev/", "")                            
                                subs['OS'] = ""                            
                            else:
                                #Not enough space, don't write the name
                                subs['path'] = ""                          
                                subs['OS'] = ""
                            subs['color'] = color                            
                            if (space == 0):
                                space = 1
                            subs['space'] = space
                            subs['title'] = display_name + "\n" + last_added_partition.description
                            if "%" in last_added_partition.used_space:               
                                subs['usage'] = last_added_partition.used_space.strip()
                            self.partitions.append(last_added_partition)
                            
                    partition = partition.nextPartition()
            self.treeview.set_model(model)
        except Exception, e:
            print e
            
    def prepare(self):
        self.installer.can_go_back(True)
        self.installer.can_go_forward(True)
        
    def get_title(self):
        return _("Where should we install?")

    def get_name(self):
        return "disks"

    def get_icon_name(self):
        return "drive-harddisk-system-symbolic"

    def get_primary_answer(self):
        return "Not yet implemented"
