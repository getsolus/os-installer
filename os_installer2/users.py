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


""" Allowed regex for a username """
USERNAME_REGEX = "^[a-z_][a-z0-9_-]*[$]?$"

""" Minimum password length """
PASSWORD_LENGTH = 6


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
