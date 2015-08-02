import pytests

uses_async = pytest.mark.skipif(
    sys.version_info < (3, 4),
    reason="async tests require python 3.4+")
