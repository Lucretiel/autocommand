from inspect import signature, Signature, Parameter
import pytest
from autocommand.autoparse import KWArgError, PositionalArgError, make_parser


def test_kwargs(check_parse):
    def func(**kwargs): pass

    with pytest.raises(KWArgError):
        make_parser(signature(func), "", "", False)


def test_positional(check_parse):
    # We have to fake this one, because it isn't possible to create a
    # positional-only parameter in pure python

    with pytest.raises(PositionalArgError):
        make_parser(
            Signature([Parameter('arg', Parameter.POSITIONAL_ONLY)]),
            "", "", False)
