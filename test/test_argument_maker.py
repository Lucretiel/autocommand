from argparse import ArgumentParser
from inspect import Parameter
from pytest import mark
from unittest.mock import Mock
from io import IOBase

from autocommand import _make_argument


def param(**kwargs):
    '''
    Create a inspect.Parameter with the (default) kind POSITIONAL_OR_KEYWORD
    '''
    kwargs.setdefault('kind', Parameter.POSITIONAL_OR_KEYWORD)
    return Parameter(**kwargs)

fakefile = Mock(IOBase)

arg_cases = [
    # Basic argument
    (param(name='arg'),
        {}),
    # Typed argument
    (param(name='arg', annotation=int),
        {'type': int}),

    # Basic option
    (param(name='arg', default=None),
        {'default': None, 'dest': 'arg'}),

    # Bool argument
    (param(name='arg', annotation=bool),
        {'action': 'store_true', 'dest': 'arg'}),
    # True option
    (param(name='arg', default=True),
        {'action': 'store_false', 'dest': 'arg', 'default': True}),
    # False option
    (param(name='arg', default=False),
        {'action': 'store_true', 'dest': 'arg', 'default': False}),

    # Implicitly typed default option
    (param(name='arg', default=0),
        {'default': 0, 'dest': 'arg', 'type': int}),

    # File type
    (param(name='arg', default=fakefile),
        {'default': fakefile, 'dest': 'arg', 'type': str}),

    # Description
    (param(name='arg', annotation="description text"),
        {'help': "description text"}),

    # Description + type
    (param(name='arg', annotation=("description text", int)),
        {'help': "description text", "type": int}),

    # Positional
    (param(name='args', kind=Parameter.VAR_POSITIONAL),
        {'nargs': '*'}),

    # Typed positional
    (param(name='args', kind=Parameter.VAR_POSITIONAL, annotation=int),
        {'nargs': '*', 'type': int}),
]


@mark.parametrize('param, kwargs', arg_cases)
def test_make_arguments(param, kwargs):
    made_args, made_kwargs = _make_argument(param, set())

    assert made_kwargs == kwargs

flag_cases = [
    # Basic option
    (param(name='arg', default=None), [],
        ['-a', '--arg'], {'a'}),

    # Cased option
    (param(name='arg', default=None), ['a'],
        ['-A', '--arg'], {'a', 'A'}),

    # Downcased option
    (param(name='ARG', default=None), ['A'],
        ['-a', '--ARG'], {'a', 'A'}),

    # Unavailable option
    (param(name='arg', default=None), ['a', 'A'],
        ['--arg'], {'a', 'A'}),

    # Single char
    (param(name='a', default=None), [],
        ['-a'], {'a'}),

    # Cased char
    (param(name='a', default=None), ['a'],
        ['-A'], {'a', 'A'}),

    # Unavailable char
    (param(name='a', default=None), ['a', 'A'],
        ['--a'], {'a', 'A'})
]


@mark.parametrize('param, used, flags, new_used', flag_cases)
def test_flag_creation(param, used, flags, new_used):
    # Ensure transitivity: copy the set
    used = set(used)
    made_args, made_kwargs = _make_argument(param, used)

    assert made_args == flags
    assert used == new_used
