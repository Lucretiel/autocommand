from io import IOBase
from sys import stdout

from pytest import yield_fixture, raises
from autocommand import smart_open


HELLO_CONTENTS = "Hello, World!\n"


@yield_fixture
def hello_filepath(tmpdir):
    '''
    Create a file called 'hello.txt' in tmpdir. This file has the contents
    "Hello, World!\\n". The fixture returns the path to the file as a string.
    '''
    file_path = tmpdir.join("hello.txt")
    file_path.write(HELLO_CONTENTS)
    yield str(file_path)
    file_path.remove()


@yield_fixture
def hello_file(hello_filepath):
    '''
    Returns an opened file as from hello_filepath
    '''
    with open(hello_filepath) as file:
        yield file


def test_path(hello_filepath):
    assert isinstance(hello_filepath, str)

    with smart_open(hello_filepath) as file:
        contents = file.read()
        assert contents == HELLO_CONTENTS

    assert file.closed is True


def test_file(hello_file):
    assert isinstance(hello_file, IOBase)
    assert hello_file.closed is False

    with smart_open(hello_file) as file:
        contents = file.read()
        assert contents == HELLO_CONTENTS

    assert file.closed is False


def test_nonexistent(tmpdir):
    file_path = tmpdir.join('goodbye.txt')

    with raises(FileNotFoundError):
        with smart_open(str(file_path)) as file:
            pass
