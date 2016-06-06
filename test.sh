#!/bin/bash

pep8 os-installer-gtk  os_installer2/*.py os_installer2/pages/*.py || exit 1
flake8 os-installer-gtk  os_installer2/*.py os_installer2/pages/*.py || exit 1

# check use of %s
grep '%s' os-installer-gtk os_installer2/*.py os_installer2/pages/*.py && exit 1
