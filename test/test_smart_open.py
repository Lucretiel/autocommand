from autocommand import smart_open
from pytest import raises, fixture, yield_fixture
from unittest.mock import patch, MagicMock
from io import IOBase


def mockfile():
    return MagicMock(IOBase)


def patch_open(*args, **kwargs):
    return patch('builtins.open', *args, return_value=mockfile(), **kwargs)


def test_path():
    '''
    Test smart_open with a file path. It the file should be opened, then closed
    at the end of the context.
    '''
    with patch_open() as mock_open:
        with smart_open('/path/to/file') as file:
            file.readline()

    mock_open.assert_called_once_with('/path/to/file')
    file.__enter__.assert_called_once_with()
    file.readline.assert_called_once_with()
    file.__exit__.assert_called_once_with(None, None, None)


def test_file():
    '''
    Test smart_open with NOT a file path. The input object should be returned,
    and no context methods should be called on it
    '''
    fakefile = mockfile()
    # For some reason open(MagicMock()) doesn't throw, so we have to mock open

    with patch_open(side_effect=TypeError):
        with smart_open(fakefile) as file:
            file.readline()

    assert file is fakefile
    assert not file.__enter__.called
    file.readline.assert_called_once_with()
    assert not file.__enter__.called


def test_open_args(tmpdir):
    '''
    Test that smart_open can forward kwargs correctly to open.
    '''
    with patch_open() as mock_open:
        with smart_open('/path/to/file', 'w', encoding='utf8') as file:
            pass

    mock_open.assert_called_once_with('/path/to/file', 'w', encoding='utf8')
