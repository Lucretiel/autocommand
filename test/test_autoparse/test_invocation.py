from unittest.mock import patch
from argparse import ArgumentParser
import pytest
from autocommand.autoparse import autoparse, TooManySplitsError


def test_basic_invocation():
    @autoparse
    def func(arg1, arg2: int, opt1=None, opt2=2, opt3='default', flag=False):
        return arg1, arg2, opt1, opt2, opt3, flag

    arg1, arg2, opt1, opt2, opt3, flag = func(
        ['value1', '1', '-o', 'hello', '--opt2', '10', '-f'])

    assert arg1 == 'value1'
    assert arg2 == 1
    assert opt1 == 'hello'
    assert opt2 == 10
    assert opt3 == 'default'
    assert flag is True


def test_invocation_from_argv():
    @autoparse
    def func(arg1, arg2: int):
        return arg1, arg2

    with patch('sys.argv', ['command', '1', '2']):
        arg1, arg2 = func()
        assert arg1 == "1"
        assert arg2 == 2


def test_description_epilog_help(check_help_text):
    @autoparse(
        description='this is a description',
        epilog='this is an epilog')
    def func(arg: 'this is help text'):
        pass

    check_help_text(
        lambda: func(['-h']),
        'this is a description',
        'this is an epilog',
        'this is help text')


def test_docstring_description(check_help_text):
    @autoparse
    def func(arg):
        '''This is a docstring description'''
        pass

    check_help_text(
        lambda: func(['-h']),
        'This is a docstring description')


def test_docstring_description_epilog(check_help_text):
    @autoparse
    def func(arg):
        '''
        This is the description
        -------
        This is the epilog
        '''
        pass

    created_parser = func.parser
    assert 'This is the description' in created_parser.description
    assert 'This is the epilog' in created_parser.epilog

    check_help_text(
        lambda: func(['-h']),
        'This is the description',
        'This is the epilog',
        reject='-------')


def test_bad_docstring():
    with pytest.raises(TooManySplitsError):
        @autoparse
        def func(arg):
            '''
            Part 1
            -------
            Part 2
            -------
            Part 3
            '''
            pass


def test_custom_parser():
    parser = ArgumentParser()

    parser.add_argument('arg', nargs='?')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-v', '--verbose', action='store_true')
    group.add_argument('-q', '--quiet', action='store_true')

    @autoparse(parser=parser)
    def main(arg, verbose, quiet):
        return arg, verbose, quiet

    assert main([]) == (None, False, False)
    assert main(['thing']) == ('thing', False, False)
    assert main(['-v']) == (None, True, False)
    assert main(['-q']) == (None, False, True)
    assert main(['-v', 'thing']) == ('thing', True, False)

    with pytest.raises(SystemExit):
        main(['-v', '-q'])
