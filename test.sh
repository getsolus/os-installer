#!/bin/bash

pep8 disk-test.py os-installer-gtk  os_installer2/*.py os_installer2/pages/*.py || exit 1
flake8 disk-test.py os-installer-gtk  os_installer2/*.py os_installer2/pages/*.py || exit 1
