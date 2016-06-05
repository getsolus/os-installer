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


class User:
    """ Nothing fancifull here, just a user object creation thinger """

    # System username
    username = None

    # Real name (i.e. GECOS)
    realname = None

    # Chosen password
    password = None

    # Administrator? i.e. sudo
    admin = False

    # Autologin? Not yet implemented..
    autologin = False

    def __init__(self, username, realname, password, autologin, admin):
        """ Create a new user with the given fields """
        self.username = username
        self.realname = realname
        self.password = password
        self.autologin = autologin
        self.admin = admin
