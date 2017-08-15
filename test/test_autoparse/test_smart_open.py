from autocommand.autoparse import smart_open


def test_smart_open_is_exported():
    import autocommand

    assert autocommand.smart_open is smart_open


def test_smart_open_path_read(tmpdir):
    target = tmpdir.join('file.txt')
    target.write("Hello")

    with smart_open(str(target)) as file:
        assert not file.closed
        assert file.read() == "Hello"

    assert file.closed


def test_smart_open_path_write(tmpdir):
    target = tmpdir.join('file.txt').ensure(file=True)

    with smart_open(str(target), 'w') as file:
        assert not file.closed
        file.write("Test Content")  # Tests that the file is writable

    assert file.closed
    assert target.read() == "Test Content"


def test_smart_open_path_create(tmpdir):
    target = tmpdir.join("file.txt")

    with smart_open(str(target), 'w') as file:
        file.write("Test Content")

    assert target.read() == "Test Content"


def test_smart_open_file(tmpdir):
    path = str(tmpdir.join('file.txt').ensure(file=True))

    with open(path) as file:
        with smart_open(file) as smart_file:
            assert file is smart_file
            assert not smart_file.closed
        assert not smart_file.closed
