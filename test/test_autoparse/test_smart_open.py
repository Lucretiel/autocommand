from autocommand.autoparse import smart_open


def test_smart_open_is_exported():
    import autocommand

    assert autocommand.smart_open is smart_open


def test_smart_open_path(tmpdir):
    path = str(tmpdir.join('file.txt').ensure(file=True))

    with smart_open(path, 'w') as file:
        assert not file.closed
    assert file.closed


def test_smart_open_file(tmpdir):
    path = str(tmpdir.join('file.txt').ensure(file=True))

    with open(path) as file:
        with smart_open(file) as smart_file:
            assert file is smart_file
            assert not smart_file.closed
        assert not smart_file.closed
