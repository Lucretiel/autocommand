import pytest


def test_basic_positional(check_parse):
    def func(arg): pass

    check_parse(
        func,
        "foo",
        arg="foo")


@pytest.mark.parametrize('cli_args', [
    [],
    ['value'],
    ['value1', 'value2']
])
def test_variadic_positional(check_parse, cli_args):
    check_parse(
        lambda arg1, *args: None,
        'arg1_value', *cli_args,
        arg1='arg1_value', args=cli_args)


def test_optional_default(check_parse):
    check_parse(
        lambda arg="default_value": None,
        arg="default_value")


@pytest.mark.parametrize('flags, result', [
    ([], False),
    (['-f'], True),
    (['--no-flag'], False),
    (['--no-flag', '-f'], True),
    (['--flag', '--no-flag'], False)
])
def test_add_nos(check_parse, flags, result):
    def func(flag: bool): pass

    check_parse(
        func,
        *flags,
        add_nos=True,
        flag=result)
