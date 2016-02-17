# Copyright 2014-2016 Nathan West
#
# This file is part of autocommand.
#
# autocommand is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# autocommand is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with autocommand.  If not, see <http://www.gnu.org/licenses/>.

import pytest
from autocommand.automain import automain, AutomainRequiresModuleError


@pytest.mark.parametrize('module_name', ['__main__', True])
def test_name_equals_main_or_true(module_name):
    with pytest.raises(SystemExit):
        @automain(module_name)
        def main():
            return 0


def test_name_not_main_or_true():
    def main():
        return 0

    wrapped_main = automain('some_module')(main)

    assert wrapped_main is main


def test_invalid_usage():
    with pytest.raises(AutomainRequiresModuleError):
        @automain
        def main():
            return 0


def test_args():
    main_called = False
    with pytest.raises(SystemExit):
        @automain(True, args=[1, 2])
        def main(a, b):
            nonlocal main_called
            main_called = True
            assert a == 1
            assert b == 2
    assert main_called


def test_args_and_kwargs():
    main_called = False
    with pytest.raises(SystemExit):
        @automain(True, args=[1], kwargs={'b': 2})
        def main(a, b):
            nonlocal main_called
            main_called = True
            assert a == 1
            assert b == 2

    assert main_called
