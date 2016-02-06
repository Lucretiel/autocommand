import pytest
from autocommand.autoparse import AnnotationError


def test_all_annotation_types(check_parse, check_help_text):
    def func(
        int_arg: int,
        note_arg: "note_arg description",
        note_int: ("note_int description", int),
        int_note: (int, "int_note description")): pass

    check_help_text(
        lambda: check_parse(func, '-h'),
        "note_arg description",
        "note_int description",
        "int_note description")

    check_parse(
        func,
        "1", "2", "3", "4",
        int_arg=1, note_arg="2", note_int=3, int_note=4)


@pytest.mark.parametrize('bad_annotation', [
    1000,  # An int? What?
    {'foo': 'bar'},  # A dict isn't any better
    [int, 'fooo'],  # For implementation ease we do ask for a tuple
    (),  # Though the tuple should have things in it
    (int,),  # More things
    (int, 'hello', 'world'),  # TOO MANY THINGS
    (int, int),  # The wrong kinds of things
    ("hello", "world"),  # Nope this is bad too
])
def test_bad_annotation(bad_annotation, check_parse):
    def func(arg: bad_annotation): pass

    with pytest.raises(AnnotationError):
        check_parse(func)
