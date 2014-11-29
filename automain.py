from sys import exit, argv as sys_argv
from inspect import signature
from argparse import ArgumentParser
from functools import wraps
from contextlib import contextmanager
from io import IOBase

def _apply(result_type):
    '''
    Convert the return value of a function to a different result type. Useful
    for making generators return containers.
    '''
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return result_type(func(*args, **kwargs))
        return wrapper
    return decorator


def _get_type_description(annotation):
    '''
    Given an annotation, return the type and/or description for the parameter
    '''
    if isinstance(annotation, type):
        return annotation, None
    elif isinstance(annotation, str):
        return None, annotation
    elif isinstance(annotation, tuple):
        arg1, arg2 = annotation
        if isinstance(arg1, type) and isinstance(arg2, str):
            return arg1, arg2
        elif isinstance(arg1, str) and isinstance(arg2, type):
            return arg2, arg1

    raise ValueError(
        'parameter annotation must be type, description, or tuple of both',
        annotation)


@_apply(dict)
def _get_arg_spec(param):
    '''
    For a parameter, return the kwargs to add_argument for the parameter. The
    kwargs may contain extra implementation stuff for automain, which is popped
    out pefore passed to add_argument
    '''

    # Get the type and default from the annotation.
    arg_type, description = _get_type_description(param.annotation)

    # Get the default value
    default = param.default

    # If there is no explicit type, and the default is present and not None,
    # infer the type from the default.
    if arg_type is None and param.default not in (param.empty, None):
        arg_type = type(default)

    # Special case for bool: make it just a switch
    if arg_type is bool:
        if default is not param.empty:
            yield 'default', default

        yield '_option', True
        if not default or default is param.empty:
            yield 'action', 'store_true'
        else:
            yield 'action', 'store_false'

    # Special case or IOBase: make it a string, for a filename.
    elif isinstance(default, IOBase):
        yield 'default', default
        if issubclass(arg_type, IOBase):
            yield 'type', str
        else:
            yield 'type', arg_type
        yield '_option', True

    # Everything else: yield type and default
    else:
        if default is not param.empty:
            yield '_option', True
            yield 'default', default
        if arg_type is not None:
            yield 'type', arg_type

    # nargs: if the signature includes *args, collect them as trailing CLI
    # arguments in a list.
    if param.kind is param.VAR_POSITIONAL:
        yield 'nargs', '*'

    # DESCRIPTION
    if description is not None:
        yield 'help', description

    # TODO: special case for list type.
    #   - How to specificy type of list members?
    #   - action='append' vs nargs='*'

    # TODO: special case for default=sys.stdin and friends.
    #   - type - should be str, something else?
    #   - check for file existence?
    #   - find a way to make it an argument instead of an option
    #   - how to allow for explicit type if provided, but not use type(default)


@_apply(tuple)
def _get_arg_flags(name, is_option, used_char_args):
    '''
    For a parameter, get the flags to add_argument for the parameter.

    name: the name of the argument
    is_option: if True, will return -o and --option flags.
    used_char_args: set of characters used to prevent reuse of -o options.
    '''
    # NOTE: it is critical that the logic for this function be deterministic.
    # Be careful when using sets or dicts

    # TODO: smarter logic: allow for --config/-C, etc. This will require
    # figuring out the different permutations of flag/dest/metavar.
    if is_option:
        if name[0] not in used_char_args:
            used_char_args.add(name[0])
            yield '-{}'.format(name[0])
        yield '--{}'.format(name)
    else:
        yield name


def _add_argument(parser, param, used_char_args):
    if param.kind is param.POSITIONAL_ONLY:
        raise ValueError("parameter must have a name", param)
    elif param.kind is param.VAR_KEYWORD:
        raise ValueError("automain doesn't understand kwargs", param)

    arg_spec = _get_arg_spec(param)

    flags = _get_arg_flags(
        param.name,
        arg_spec.pop('_option', False),
        used_char_args)

    return parser.add_argument(*flags, **arg_spec)


def _add_arguments(parser, params):
    used_char_args = {'h'}

    for param in params.values():
        _add_argument(parser, param, used_char_args)


@contextmanager
def smart_open(filename_or_file, *args, **kwargs):
    '''
    This context manager allows you to correctly open a filename, if there's a
    chance you want some already-existing file object, like sys.stdout. If the
    filename argument is a str, the file is opened, sent to the context, and
    closed at the end of the context, just like "with open(filename) as f". If
    it isn't a str, the object simply sent to the context unchanged. Example:

        def work_with_file(name=sys.stdout):
            with smart_open(name) as f:
                print("Some stuff", file=f)
    '''
    if isinstance(filename_or_file, str):
        with open(filename_or_file, *args, **kwargs) as f:
            yield f
    else:
        yield filename_or_file


def automain(module, description=None, epilog=None):
    '''
    Decorator to create an automain function. The function's signature is
    analyzed, and an ArgumentParser is created, using the `description` and
    `epilog` parameters, to parse command line arguments corrosponding to the
    function's parameters. The function's signature is changed to accept a
    single argv parameter, as from sys.argv, though you can supply your own.
    When called, the function parses the arguments provided, then supplies them
    to the decorated function. Keep in mind that this happens with plain
    argparse, so supplying invalid arguments or '-h' will cause SystemExit to
    be raised.

    If `module` == "__main__", the decorated function is called immediately
    with sys.argv, and the progam is exited with the return value; this is so
    that you can call @automain(__name__) and be able to import the module for
    testing.

    The decorated function is attached to the result as the `main` attribute. False
    '''
    def decorator(main):
        parser = ArgumentParser(description=description, epilog=epilog)
        main_sig = signature(main)
        _add_arguments(parser, main_sig.parameters)

        def main_wrapper(argv):
            parser.prog = argv[0]
            function_args = main_sig.bind_partial()
            function_args.arguments.update(vars(parser.parse_args(argv[1:])))
            return main(*function_args.args, **function_args.kwargs)

        main_wrapper.main = main

        if module == '__main__':
            exit(main_wrapper(sys_argv))

        return main_wrapper
    return decorator



