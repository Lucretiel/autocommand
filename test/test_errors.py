import autocommand
from inspect import Parameter, Signature
from unittest.mock import patch
from pytest import raises, mark


# Note: The (int, 1) case is to provide 100% branch coverage
@mark.parametrize('annotation', [1, (int, 1)])
def test_annotation_error(annotation):
    with raises(autocommand.AnnotationError):
        @autocommand.autocommand
        def annotate(arg1: annotation):
            pass


def test_kwarg_error():
    with raises(autocommand.KWArgError):
        @autocommand.autocommand
        def kwarg(**kwargs):
            pass


def test_positional_error():
    fake_parameter = Parameter(name='arg', kind=Parameter.POSITIONAL_ONLY)
    fake_sig = Signature([fake_parameter])

    # autocommand uses from ... import ...
    with patch('autocommand.signature', return_value=fake_sig):
        with raises(autocommand.PositionalArgError):
            @autocommand.autocommand
            def positional(arg):
                pass
