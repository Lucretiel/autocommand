#!/bin/sh

set -x

exec py.test --cov src --cov-report term-missing --cov-config .coveragerc test
