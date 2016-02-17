import pytest


@pytest.mark.parametrize("cli_args", [
    ['-aFoo'],
    ['-a', 'Foo'],
    ['--arg=Foo'],
    ['--arg', 'Foo']
])
def test_optional_flag_styles(check_parse, cli_args):
    check_parse(
        lambda arg="default_value": None,
        *cli_args,
        arg="Foo")


def test_capitalizer(check_parse):
    check_parse(
        lambda arg1="", arg2="", arg3="": None,
        '-a', 'value1', '-A', 'value2', '--arg3', 'value3',
        arg1='value1', arg2='value2', arg3='value3')


def test_reverse_capitalizer(check_parse):
    check_parse(
        lambda Arg1="", Arg2="", Arg3="": None,
        '-A', 'value1', '-a', 'value2', '--Arg3', 'value3',
        Arg1='value1', Arg2='value2', Arg3='value3')


def test_single_letter_param(check_parse):
    def func(a=''):
        pass

    check_parse(
        func,
        '-a', 'value',
        a='value')

    with pytest.raises(SystemExit):
        check_parse(
            func,
            '--a', 'value',
            a='value')


def test_single_letter_prioritized(check_parse):
    '''
    Check that, when deciding which flags get to have single-letter variants,
    single-letter function parameters are assigned a letter first, so they
    aren't recapitalized or forced to have double-dash flags.
    '''
    check_parse(
        lambda arg1='', arg2='', a='': None,
        '-a', 'value1', '-A', 'value2', '--arg2', 'value3',
        a='value1', arg1='value2', arg2='value3')


def test_h_reserved(check_parse):
    check_parse(
        lambda hello='': None,
        '-H', 'value',
        hello='value')
