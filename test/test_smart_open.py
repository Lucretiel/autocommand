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
    '''
    Test smart_open with a file path. It the file should be opened, then closed
    at the end of the context.
    '''
    assert isinstance(hello_filepath, str)

    with smart_open(hello_filepath) as file:
        contents = file.read()
        assert contents == HELLO_CONTENTS

    assert file.closed is True


def test_file(hello_file):
    '''
    Test smart_open with an open file object. The file object should be directly
    passed to the with context, and not be closed at the end.
    '''
    assert isinstance(hello_file, IOBase)
    assert hello_file.closed is False

    with smart_open(hello_file) as file:
        contents = file.read()
        assert contents == HELLO_CONTENTS
        assert file is hello_file

    assert file.closed is False


def test_nonexistent(tmpdir):
    '''
    Test that smart_open still raises exceptions, just like the open builtin.
    '''
    with raises(FileNotFoundError):
        with smart_open(str(tmpdir.join('goodbye.txt'))) as file:
            pass

def test_open_args(tmpdir):
    '''
    Test that smart_open can forward kwargs correctly to open.
    '''
    file_path = str(tmpdir.join('test.txt'))

    with smart_open(file_path, mode='w') as file:
        file.write(HELLO_CONTENTS)

    with smart_open(file_path) as file:
        contents = file.read()
        assert contents == HELLO_CONTENTS
