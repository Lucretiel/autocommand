from unittest.mock import patch, sentinel
import pytest
from argparse import ArgumentParser
from autocommand import autocommand


@pytest.mark.parametrize('module_name', ['__main__', True])
def test_name_main(module_name):
    '''
    Test that applying the autocommand decorator to a function with '__name__'
    or True as the argument causes it to be called with sys.argv, and then
    exited with the return value of the function.
    '''

    with patch('sys.argv', ['prog', 'foo', '0']):
        try:
            @autocommand(module_name)
            def prog(arg1, arg2: int):
                assert arg1 == 'foo'
                assert arg2 == 0
                return sentinel.exit_code

        except SystemExit as e:
            assert e.code is sentinel.exit_code
        else:
            pytest.fail("autocommand function didn't exit")


def test_main_attr():
    @autocommand
    def prog(arg1=False):
        return arg1

    func = prog.main

    assert func() == False
    assert func(True) == True
    assert func(arg1=10) == 10
    assert prog() == False
    assert prog('--arg1') == True


def test_docstring(capsys):
    @autocommand
    def prog():
        '''
        This is the
        help text
        '''

    with pytest.raises(SystemExit):
        prog('-h')

    out, err = capsys.readouterr()
    assert "This is the help text" in out
    assert prog.parser.description == "This is the\nhelp text"


def test_desc_epilog(capsys):
    @autocommand(
        description="This is the description",
        epilog="This is the epilog")
    def prog():
        pass

    with pytest.raises(SystemExit):
        prog('-h')

    out, err = capsys.readouterr()
    assert "This is the description" in out
    assert "This is the epilog" in out
    assert prog.parser.description == "This is the description"
    assert prog.parser.epilog == "This is the epilog"


def test_custom_parser():
    '''
    Test a custom parser. The parser includes features that can't be created by
    autocommand, but should autocommand should still handle being able to parse
    and pass to the function.
    '''
    parser = ArgumentParser()
    parser.add_argument('arg', nargs='?')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-v', '--verbose', action='store_true')
    group.add_argument('-q', '--quiet', action='store_true')

    @autocommand(parser=parser)
    def prog(arg, verbose, quiet):
        return arg, verbose, quiet

    assert prog() == (None, False, False)
    assert prog('foo') == ('foo', False, False)
    assert prog('-v') == (None, True, False)
    assert prog('-q') == (None, False, True)

    with pytest.raises(SystemExit):
        prog('-v', '-q')


def test_nos():
    @autocommand(add_nos=True)
    def prog(verbose=False):
        return verbose

    assert prog() == False
    assert prog('--verbose') == True
    assert prog('--no-verbose') == False
    assert prog('--verbose', '--no-verbose') == False
    assert prog('--no-verbose', '--verbose') == True
