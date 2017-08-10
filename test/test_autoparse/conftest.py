from inspect import signature
import pytest
from autocommand.autoparse import make_parser


#  TODO: This doesn't really need to be a fixture; replace it with a normal
#  helper
@pytest.fixture(scope='session')
def check_parse():
    def check_parse_impl(function, *args, add_nos=False, **kwargs):
        '''
        Helper for generalized parser testing. This function takes a function,
        a set of positional arguments, and a set of keyword argumnets. It
        creates an argparse parser using `autocommand.autoparse:make_parser` on
        the signature of the provided function. It then parses the positional
        arguments using this parser, and asserts that the returned set of
        parsed arguments matches the given keyword arguments exactly.

        Arguments:
          - function: The function to generate a parser for
          - *args: The set of positional arguments to pass to the generated
            parser
          - add_nos: If True, "-no-" versions of the option flags will be
            created,
            as per the `autoparse` docs.
          - **kwargs: The set of parsed argument values to check for.
        '''
        parser = make_parser(
            func_sig=signature(function),
            description=None,
            epilog=None,
            add_nos=add_nos)

        parsed_args = vars(parser.parse_args(args))
        assert parsed_args == kwargs

    return check_parse_impl


@pytest.fixture
def check_help_text(capsys):
    def check_help_text_impl(func, *texts, reject=()):
        '''
        This helper checks that some set of text is written to stdout or stderr
        after the called function raises a SystemExit. It is used to test that
        the underlying ArgumentParser was correctly configured to output a
        given set of help text(s).

        func: This should be a wrapped autoparse function that causes a
          SystemExit exception to be raised (most commonly a function with the
          -h flag, or with an invalid set of positional arguments). This
          Exception should be accompanied by some kind of printout from
          argparse to stderr or stdout.
        *texts: A set of strings to test for. All of the provided strings will
          be checked for in the captured stdout/stderr using a standard
          substring search.
        reject: A string or set of strings to check do NOT exist anywhere in
          the output. Currently used as a cludge to test the docstring split
          behavior.
        '''
        with pytest.raises(SystemExit):
            func()

        out, err = capsys.readouterr()

        # TODO: be wary of argparse's text formatting
        # TODO: test that the text appears in the order given
        for text in texts:
            assert text in out or text in err

        if isinstance(reject, str):
            reject = [reject]

        for text in reject:
            assert text not in out and text not in err

    return check_help_text_impl
