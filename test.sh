#!/bin/bash

pep8 os-installer-gtk  os_installer2/*.py || exit 1
flake8 os-installer-gtk os_installer2/*.py || exit 1
