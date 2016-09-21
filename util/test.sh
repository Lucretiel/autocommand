#!/bin/sh

set -ex

python3 -m flake8 --show-source src test

py.test \
    --cov autocommand \
    --cov-report term-missing \
    --cov-config .coveragerc \
    --strict \
    "$@" test
