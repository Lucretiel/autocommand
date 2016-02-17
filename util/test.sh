#!/bin/sh

set -ex

pep8 --show-source src test

py.test \
    --cov autocommand \
    --cov-report term-missing \
    --cov-config .coveragerc \
    --strict \
    "$@" test
