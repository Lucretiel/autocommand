import pytest
import sys
from unittest.mock import patch, sentinel
from autocommand import autocommand


@pytest.fixture(scope='module')
def autocommand_module():
    return sys.modules['autocommand.autocommand']


@pytest.yield_fixture
def patched_autoparse(autocommand_module):
    with patch.object(
            autocommand_module,
            'autoparse',
            autospec=True) as autoparse:
        yield autoparse


@pytest.yield_fixture
def patched_autoasync(autocommand_module):
    with patch.object(
            autocommand_module,
            'autoasync',
            autospec=True) as autoasync:
        yield autoasync


@pytest.yield_fixture
def patched_automain(autocommand_module):
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
