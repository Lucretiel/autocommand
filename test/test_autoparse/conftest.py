import pytest
from inspect import signature
from autocommand.autoparse import make_parser


@pytest.fixture(scope='session')
def check_parse():
    def check_parse_impl(function, *args, add_nos=False, **kwargs):
        parser = make_parser(
            func_sig=signature(function),
            description=None,
            epilog=None,
            add_nos=add_nos)

        parsed_args = parser.parse_args(args)
        for key, value in kwargs.items():
            assert getattr(parsed_args, key) == value

    return check_parse_impl


# This is ostensibly session scope, but I don't know how capsys works
@pytest.fixture
def check_help_text(capsys):
    def check_help_text_impl(func, *texts):
        with pytest.raises(SystemExit):
            func()

        out, err = capsys.readouterr()

        # TODO: be wary of argparse's text formatting
        for text in texts:
            assert text in out or text in err
    return check_help_text_impl
