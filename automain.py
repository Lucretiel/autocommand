from inspect import signature
from argparse import ArgumentParser
from sys import exit, argv
from functools import wraps

def _apply(result_type):
    '''
    Decorator to convert the return value of a function to a different result
    type
    '''
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return result_type(func(*args, **kwargs))
        return wrapper
    return decorator


# TODO: find a way to separate options from trailing optional arguments. Maybe.

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

    raise SyntaxError(
        'tuple annotation must be type, description, or both in a tuple',
        annotation)


@_apply(dict)
def _process_parameter(param):
    '''
    For a parameter, yield the parameter's type, default, nargs, help
    text, and action (the kwargs of add_argument)
    '''

    arg_type, description = _get_type_description(param.annotation)

    default = param.default

    # If there is no explicit type, get from default
    if arg_type is param.empty and default is not param.empty:
        arg_type = type(default)

    # DESCRIPTION
    if description is not None:
        yield 'help', description

    if arg_type is bool:
        # Special case for bool: make it just a switch
        yield 'action', ('store_true' if default != True else 'store_false')

    else:
        if arg_type is not param.empty:
            yield 'type', arg_type
        if default is not param.empty:
            yield 'default', default

    if param.kind is param.VAR_POSITIONAL:
        yield 'nargs', '*'


def _is_option(arg_spec):
    # TODO: update this logic if necessary
    return 'action' in arg_spec or 'default' in arg_spec


@_apply(tuple)
def _get_flags(name, is_option, used_char_args):
    if is_option:
        if name[0] not in used_char_args:
            yield '-{}'.format(name[0])
            used_char_args.add(name[0])

        elif name[0].upper() not in used_char_args:
            yield '-{}'.format(name[0].upper())
            used_char_args.add(name[0].upper())

        elif name[0].lower() not in used_char_args:
            yield '-{}'.format(name[0].lower())
            used_char_args.add(name[0].lower())

        elif len(name) == 1:
            yield '--{}'.format(name)

        if len(name) > 1:
            yield '--{}'.format(name)
    else:
        yield name


def _add_argument(parser, param, used_char_args):
    if param.kind is param.POSITIONAL_ONLY:
        raise SyntaxError("parameter must have a name", param)
    elif param.kind is param.VAR_KEYWORD:
        raise SyntaxError("automain doesn't understand kwargs", param)

    arg_spec = _process_parameter(param)

    flags = _get_flags(
        param.name,
        _is_option(arg_spec),
        used_char_args)

    parser.add_argument(*flags, **arg_spec)


def automain(module, description=None, epilog=None):
    def decorator(main):
        main_sig = signature(main)
        parser = ArgumentParser(description=description, epilog=epilog)

        used_char_args = {'h'}

        for param in main_sig.parameters.values():
            _add_argument(parser, param, used_char_args)

        def main_wrapper(argv):
            function_args = main_sig.bind_partial()
            function_args.arguments.update(vars(parser.parse_args(argv)))
            return main(*function_args.args, **function_args.kwargs)

        main_wrapper.main = main

        if module == '__main__':
            exit(main_wrapper(argv[1:]))

        return main_wrapper
    return decorator



