import pytest
from autocommand.autoparse import AnnotationError


@pytest.mark.parametrize("type_object", [
    int,
    lambda value: "FACTORY({})".format(value)
])
def test_all_annotation_types(check_parse, check_help_text, type_object):
    #  type_object is either `int` or a factory function that converts "str" to
    #  "FACTORY(str)"
    def func(
        typed_arg: type_object,
        note_arg: "note_arg description",
        note_type: ("note_type description", type_object),
        type_note: (type_object, "type_note description")): pass

    check_help_text(
        lambda: check_parse(func, '-h'),
        "note_arg description",
        "note_type description",
        "type_note description")

    check_parse(
        func,
        "1", "2", "3", "4",
        typed_arg=type_object("1"),
        note_arg="2",
        note_type=type_object("3"),
        type_note=type_object("4"))


@pytest.mark.parametrize('bad_annotation', [
    1000,  # An int? What?
    {'foo': 'bar'},  # A dict isn't any better
    [int, 'fooo'],  # For implementation ease we do ask for a tuple
    (),  # Though the tuple should have things in it
    (int,),  # More things
    (int, 'hello', 'world'),  # TOO MANY THINGS
    (int, int),  # The wrong kinds of things
    ("hello", "world"),  # Nope this is bad too
    (lambda value: value, lambda value: value),  # Too many lambdas
])
def test_bad_annotation(bad_annotation, check_parse):
    def func(arg: bad_annotation): pass

    with pytest.raises(AnnotationError):
        check_parse(func)
