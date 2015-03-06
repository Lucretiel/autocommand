#!/bin/sh

exec py.test --cov src --cov-report term-missing --cov-config .coveragerc test
