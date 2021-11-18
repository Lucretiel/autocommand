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
import sys
from unittest.mock import patch, sentinel
from autocommand import autocommand


autocommand_module = sys.modules['autocommand.autocommand']


def _asyncio_unavailable():
    try:
        import asyncio

        # This is here to silence flake8 complaining about "unused import"
        assert asyncio
    except ImportError:
        return True
    else:
        return False


skip_if_async_unavailable = pytest.mark.skipif(
    _asyncio_unavailable(),
    reason="async tests require asyncio (python3.4+)")


@pytest.fixture
def patched_autoparse():
    with patch.object(
            autocommand_module,
            'autoparse',
            autospec=True) as autoparse:
        yield autoparse


@pytest.fixture
def patched_autoasync():
    with patch.object(
            autocommand_module,
            'autoasync',
            create=True) as autoasync:
        if sys.version_info < (3, 4):
            autoasync.side_effect = NameError('autoasync')

        yield autoasync


@pytest.fixture
def patched_automain():
    with patch.object(
            autocommand_module,
            'automain',
            autospec=True) as automain:

        yield automain


def test_autocommand_no_async(
        patched_automain,
        patched_autoasync,
        patched_autoparse):

    autocommand_wrapped = autocommand(
        sentinel.module,
        description=sentinel.description,
        epilog=sentinel.epilog,
        add_nos=sentinel.add_nos,
        parser=sentinel.parser)(sentinel.original_function)

    assert not patched_autoasync.called

    patched_autoparse.assert_called_once_with(
        sentinel.original_function,
        description=sentinel.description,
        epilog=sentinel.epilog,
        add_nos=sentinel.add_nos,
        parser=sentinel.parser)

    autoparse_wrapped = patched_autoparse.return_value

    patched_automain.assert_called_once_with(sentinel.module)
    patched_automain.return_value.assert_called_once_with(autoparse_wrapped)

    automain_wrapped = patched_automain.return_value.return_value
    assert automain_wrapped is autocommand_wrapped


@pytest.mark.parametrize(
    'input_loop, output_loop',
    [(sentinel.loop, sentinel.loop),
     (True, None)])
@skip_if_async_unavailable
def test_autocommand_with_async(
        patched_automain,
        patched_autoasync,
        patched_autoparse,
        input_loop, output_loop):

    autocommand_wrapped = autocommand(
        sentinel.module,
        description=sentinel.description,
        epilog=sentinel.epilog,
        add_nos=sentinel.add_nos,
        parser=sentinel.parser,
        loop=input_loop,
        forever=sentinel.forever,
        pass_loop=sentinel.pass_loop)(sentinel.original_function)

    patched_autoasync.assert_called_once_with(
        sentinel.original_function,
        loop=output_loop,
        forever=sentinel.forever,
        pass_loop=sentinel.pass_loop)
    autoasync_wrapped = patched_autoasync.return_value

    patched_autoparse.assert_called_once_with(
        autoasync_wrapped,
        description=sentinel.description,
        epilog=sentinel.epilog,
        add_nos=sentinel.add_nos,
        parser=sentinel.parser)
    autoparse_wrapped = patched_autoparse.return_value

    patched_automain.assert_called_once_with(sentinel.module)
    patched_automain.return_value.assert_called_once_with(autoparse_wrapped)
    automain_wrapped = patched_automain.return_value.return_value
    assert automain_wrapped is autocommand_wrapped


def test_autocommand_incorrect_invocation_no_parenthesis(
        patched_automain,
        patched_autoparse,
        patched_autoasync):
    '''
    Test that an exception is raised if the autocommand decorator is called
    without parenthesis by accident
    '''

    with pytest.raises(TypeError):
        @autocommand
        def original_function():
            pass
