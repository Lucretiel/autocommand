import autocommand
from inspect import Parameter
import pytest


@pytest.mark.parametrize('annotation, type, description', [
    (Parameter.empty,      None, None),
    (int,                  int, None),
    ('description',        None, 'description'),
    ((int, 'description'), int, 'description'),
    (('description', int), int, 'description')])
def test_annotation(annotation, type, description):
    assert autocommand._get_type_description(annotation) == (type, description)


def test_invalid_annotation():
    with pytest.raises(autocommand.AnnotationError):
        autocommand._get_type_description(None)
