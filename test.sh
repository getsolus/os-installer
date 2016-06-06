#!/bin/bash

pep8 os-installer-gtk  os_installer2/*.py os_installer2/pages/*.py || exit 1
flake8 os-installer-gtk  os_installer2/*.py os_installer2/pages/*.py || exit 1

# check use of %s
t=`grep '%s' os-installer-gtk os_installer2/*.py os_installer2/pages/*.py | grep -v tz.py`
if [[ $t == "" ]]; then
    exit 0
fi
echo "Found use of '%s' in tree"
echo "$t"
exit 1
