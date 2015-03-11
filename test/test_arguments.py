from contextlib import contextmanager
from autocommand import autocommand
import pytest
from pytest import raises
from functools import wraps


def run_autocmd_tests(*cases):
    '''
    This decorator wraps up a bunch of test cases for an autocommand function.
    It basically works like this:

    @run_autcommand_tests(
        ('--arg 1',   1),
        ('-a 1',      1)
        ('--arg foo', SystemExit))
    def test_int_option(arg=0):
        return arg

    The test_int_option is internally converted into an autocommand function,
    then the function is turned into a test case. The test case runs each set
    of options (which have .split() called on them) on the autocommand and
    checks that the return value matches. If `SystemExit` is used, the program
    is checked instead that it raises a SystemExit.
    '''
    def decorator(func):
        def test_wrapper():
            prog = autocommand(func)
            for args, result in cases:
                args = args.split()
                if result is SystemExit:
                    with raises(SystemExit):
                        prog(*args)
                else:
                    assert prog(*args) == result
        return test_wrapper
    return decorator


@run_autocmd_tests(
    ('', 0),
    ('arg', SystemExit))
def test_no_args():
    return 0


@run_autocmd_tests(
    ('', SystemExit),
    ('arg', 'arg'))
def test_single_arg(arg1):
    return arg1


@run_autocmd_tests(
    ('arg', SystemExit),
    ('1', 1))
def test_int_arg(arg1: int):
    return arg1


@run_autocmd_tests(
    ('',        []),
    ('foo',     ['foo']),
    ('foo bar', ['foo', 'bar']))
def test_var_args(*args):
    return list(args)


@run_autocmd_tests(
    ('',    []),
    ('foo', SystemExit),
    ('1',   [1]),
    ('1 2', [1, 2]))
def test_typed_var_args(*args: int):
    return list(args)


@run_autocmd_tests(
    ('',          None),
    ('--arg foo', 'foo'),
    ('-a foo',    'foo'),
    ('--arg=foo', 'foo'),
    ('-afoo',     'foo'))
def test_simple_option(arg=None):
    return arg


@run_autocmd_tests(
    ('',          None),
    ('--arg foo', SystemExit),
    ('--arg 1',   1))
def test_typed_int_option(arg: int =None):
    return arg
