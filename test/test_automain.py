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
    main_called = False
    with pytest.raises(SystemExit):
        @automain(True, args=[1, 2])
        def main(a, b):
            nonlocal main_called
            main_called = True
            assert a == 1
            assert b == 2
    assert main_called


def test_args_and_kwargs():
    main_called = False
    with pytest.raises(SystemExit):
        @automain(True, args=[1], kwargs={'b': 2})
        def main(a, b):
            nonlocal main_called
            main_called = True
            assert a == 1
            assert b == 2

    assert main_called
