import pytest
from autocommand.automain import automain, AutomainRequiresModuleError


@pytest.mark.parametrize('module_name', ['__main__', True])
def test_name_equals_main_or_true(module_name):
    with pytest.raises(SystemExit):
        @automain(module_name)
        def main():
            return 0


def test_name_not_main_or_true():
    def main():
        return 0

    wrapped_main = automain('some_module')(main)

    assert wrapped_main is main


def test_invalid_usage():
    with pytest.raises(AutomainRequiresModuleError):
        @automain
        def main():
            return 0


def test_args():
    with pytest.raises(SystemExit) as exc_info:
        @automain(True, args=[1, 2, 3])
        def main(a, b, c):
            assert a == 1
            assert b == 2
            assert c == 3


def test_kwargs():
    with pytest.raises(SystemExit) as exc_info:
        @automain(True, kwargs={'a': 1, 'b': 2, 'c': 3})
        def main(a, b, c):
            assert a == 1
            assert b == 2
            assert c == 3
