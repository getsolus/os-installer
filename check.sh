#!/bin/bash

if [[ -e "check.log" ]]; then
    rm check.log
fi

pep8-3.4 `find . -name "*.py" -type f` 2>&1 | tee check.log
