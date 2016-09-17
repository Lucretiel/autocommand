import pytest


def test_int_positional(check_parse):
    def func(arg: int): pass

    check_parse(
        func,
        "1",
        arg=1)

    with pytest.raises(SystemExit):
        check_parse(
            func,
            'hello')


def test_int_default(check_parse):
    def func(arg=10): pass

    check_parse(func, "-a1", arg=1)
    check_parse(func, arg=10)
    with pytest.raises(SystemExit):
        check_parse(func, "-aHello")


def test_int_none_default(check_parse):
    def func(arg: int =None): pass

    check_parse(func, '-a1', arg=1)
    check_parse(func, arg=None)

    with pytest.raises(SystemExit):
        check_parse(func, '-aHello')


# A note on bool types: when the type is EXPLICITLY bool, then the parameter is
# flag no matter what. If the flag is present on the CLI, the default is NOT
# used; this is the most internally consistent behavior (no flag -> default,
# flag -> nondefault). The "truthiness" of the default is used to determine
# the nondefault value- falsy values like `None`, `0`, and `[]` result in True
# being nondefault, while "truthy" values like `1`, `[1]`, and `'hello'` result
# in False being nondefault.
def make_bool_test_params():
    def bool1(flag=False): pass

    def bool2(flag=True): pass

    def bool3(flag: bool): pass

    def bool4(flag: bool =None): pass

    def bool5(flag: bool =0): pass

    def bool6(flag: bool ='noflag'): pass
    return [
        (bool1, True, False),
        (bool2, False, True),
        (bool3, True, False),
        (bool4, True, None),
        (bool5, True, 0),
        (bool6, False, 'noflag')]


@pytest.mark.parametrize(
    'function, with_flag, without_flag',
    make_bool_test_params()
)
def test_bool(check_parse, function, with_flag, without_flag):
    check_parse(function, '-f', flag=with_flag)
    check_parse(function, '--flag', flag=with_flag)
    check_parse(function, flag=without_flag)


def test_file(check_parse, tmpdir):
    filepath = tmpdir.join('test_file.txt')
    filepath.ensure(file=True)
    with filepath.open() as file:
        def func(input_file=file): pass

        check_parse(func, input_file=file)
        check_parse(func, "-i", "path/to/file", input_file="path/to/file")
