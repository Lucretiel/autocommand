#!/bin/sh

set -ex

pep8 --show-source -v src test

py.test \
	--cov autocommand \
	--cov-report term-missing \
	--cov-config .coveragerc \
	test
