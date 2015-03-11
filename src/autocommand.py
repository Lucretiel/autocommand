# Copyright 2014-2015 Nathan West
#
# This file is part of autocommand.
#
# autocommand is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# autocommand is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with autocommand.  If not, see <http://www.gnu.org/licenses/>.

from inspect import signature, Parameter, getdoc
from argparse import ArgumentParser, _StoreConstAction
from contextlib import contextmanager
from io import IOBase


__version__ = '1.0.0'


_empty = Parameter.empty


class AutocommandError(TypeError):
    '''Base class for autocommand exceptions'''


class AnnotationError(AutocommandError):
    '''Annotation error: annotation must be a string, type, or tuple of both'''


class PositionalArgError(AutocommandError):
    '''
    Postional Arg Error: autocommand can't handle postional-only parameters
    '''


class KWArgError(AutocommandError):
    '''kwarg Error: autocommand can't handle a **kwargs parameter'''


def _get_type_description(annotation):
    '''
    Given an annotation, return the (type, description) for the parameter
    '''
    if annotation is _empty:
        return None, None
    elif isinstance(annotation, type):
        return annotation, None
    elif isinstance(annotation, str):
        return None, annotation
    elif isinstance(annotation, tuple):
        arg1, arg2 = annotation
        if isinstance(arg1, type) and isinstance(arg2, str):
            return arg1, arg2
        elif isinstance(arg1, str) and isinstance(arg2, type):
            return arg2, arg1

    raise AnnotationError(annotation)


def _make_argument(param, used_char_args):
    '''
    Get the *args and **kwargs to use for parser.add_argument for a given
    parameter. used_char_args is the set of -short options currently already in
    use.
    '''
    if param.kind is param.POSITIONAL_ONLY:
        raise PositionalArgError(param)
    elif param.kind is param.VAR_KEYWORD:
        raise KWArgError(param)

    arg_spec = {}
    is_option = False

    # Get the type and default from the annotation.
    arg_type, description = _get_type_description(param.annotation)

    # Get the default value
    default = param.default

    # If there is no explicit type, and the default is present and not None,
    # infer the type from the default.
    if arg_type is None and default not in (_empty, None):
        arg_type = type(default)

    # Add default. The presence of a default means this is an option, not an
    # argument.
    if default is not _empty:
        arg_spec['default'] = default
        is_option = True

    # Add the type
    if arg_type is not None:
        # Special case for bool: make it just a --switch
        if arg_type is bool:
            if not default or default is _empty:
                arg_spec['action'] = 'store_true'
            else:
                arg_spec['action'] = 'store_false'

            # Switches are always options
            is_option = True

        # Special case for file types: make it a string type, for filename
        elif isinstance(default, IOBase):
            arg_spec['type'] = str

        # TODO: special case for list type.
        #   - How to specificy type of list members?
        #       - param: [int]
        #       - param: int =[]
        #   - action='append' vs nargs='*'

        else:
            arg_spec['type'] = arg_type

    # nargs: if the signature includes *args, collect them as trailing CLI
    # arguments in a list. *args can't have a default value, so it can never be
    # an option.
    if param.kind is param.VAR_POSITIONAL:
        # TODO: consider depluralizing metavar/name here.
        arg_spec['nargs'] = '*'

    # Add description.
    if description is not None:
        arg_spec['help'] = description

    # Get the --flags
    flags = []
    name = param.name

    if is_option:
        # Add the first letter as a -short option.
        for letter in name[0], name[0].swapcase():
            if letter not in used_char_args:
                used_char_args.add(letter)
                flags.append('-{}'.format(letter))
                break

        # If the parameter is a --long option, or is a -short option that
        # somehow failed to get a flag, add it.
        if len(name) > 1 or not flags:
            flags.append('--{}'.format(name))

        arg_spec['dest'] = name
    else:
        flags.append(name)

    return flags, arg_spec


def _make_parser(main_sig, description, epilog, add_nos):
    '''
    Given the signature of a function, create an ArgumentParser
    '''
    parser = ArgumentParser(description=description, epilog=epilog)

    used_char_args = {'h'}
    # Add each argument. Do single-character arguments first, if
    # present, so that they get priority, and don't have to get --long
    # versions. sorted is stable, so the parameters will still be in
    # relative order
    for param in sorted(
            main_sig.parameters.values(),
            key=lambda param: len(param.name) > 1):
        flags, spec = _make_argument(param, used_char_args)
        action = parser.add_argument(*flags, **spec)

        # If requested, add --no- option counterparts. Because the
        # option/argument names can't have a hyphen character, these
        # shouldn't conflict with any existing options.
        # TODO: decide if it's better, stylistically, to do these at
        # the end, AFTER all of the parameters.
        if add_nos and isinstance(action, _StoreConstAction):
            parser.add_argument(
                '--no-{}'.format(action.dest),
                action='store_const',
                dest=action.dest,
                const=action.default)
            # No need for a default=, as the first action takes
            # precedence.
    return parser


def autocommand(
        module=None, *,
        description=None,
        epilog=None,
        add_nos=False,
        parser=None):
    '''
    Decorator to create an autocommand function. The function's signature is
    analyzed, and an ArgumentParser is created, using the `description` and
    `epilog` parameters, to parse command line arguments corrosponding to the
    function's parameters. The function's signature is changed to accept *argv
    parameters, as from `sys.argv[1:]`, though you can supply your own. When
    called, the function parses the arguments provided, then supplies them to
    the decorated function. Keep in mind that this happens with plain argparse,
    so supplying invalid arguments or '-h' will cause a usage statement to be
    printed and a `SystemExit` to be raised.

    Optionally, pass a module name (typically `__name__`) as the first argument
    to `autocommand`. If you do, and it is "__main__", the decorated function
    is called immediately with sys.argv, and the progam is exited with the
    return value; this is so that you can call `@autocommand(__name__)` and
    still be able to import the module for testing.

    The `desctiption` and `epilog` parameters corrospond to the same respective
    argparse parameters. If no description is given, it defaults to the
    decorated functions's docstring, if present.

    If add_nos is True, every boolean option will have a --no- version created
    as well, which inverts the option. For instance, the --verbose option will
    have a --no-verbose counterpart. These are not mutually exclusive-
    whichever one appears last on the command line will have precedence.

    If a parser is given, it is used instead of one generated from the function
    signature.

    The decorated function is attached to the result as the `main` attribute,
    and the parser is attached as the `parser` attribute.
    '''

    # If @autocommand is used instead of @autocommand(__name__)
    if callable(module):
        return autocommand(
            description=description,
            epilog=epilog,
            add_nos=add_nos,
            parser=parser)(module)

    def decorator(main):
        main_sig = signature(main)
        local_parser = parser or _make_parser(
            main_sig, description or getdoc(main), epilog, add_nos)

        def main_wrapper(*argv):
            # Get empty argument binding, to fill with parsed arguments. This
            # object does all the heavy lifting of turning named arguments into
            # into correctly bound *args and **kwargs.
            func_args = main_sig.bind_partial()
            func_args.arguments.update(vars(local_parser.parse_args(argv)))

            return main(*func_args.args, **func_args.kwargs)

        # If we are running as a script/program, call main right away and exit.
        if module == '__main__' or module is True:
            from sys import exit, argv
            exit(main_wrapper(*argv[1:]))

        # Otherwise, attach the wrapped main function and parser, and return
        # the wrapper.
        main_wrapper.main = main
        main_wrapper.parser = local_parser
        return main_wrapper

    return decorator


@contextmanager
def smart_open(filename_or_file, *args, **kwargs):
    '''
    This context manager allows you to open a filename, if you want to default
    some already-existing file object, like sys.stdout, which shouldn't be
    closed at the end of the context. If the filename argument is a str, bytes,
    or int, the file object is created via a call to open with the given *args
    and **kwargs, sent to the context, and closed at the end of the context,
    just like "with open(filename) as f:". If it isn't one of the openable
    types, the object simply sent to the context unchanged. Example:

        def work_with_file(name=sys.stdout):
            with smart_open(name) as f:
                # Works correctly if name is a str filename or sys.stdout
                print("Some stuff", file=f)
                # If it was a filename, f is closed at the end here.
    '''
    try:
        file = open(filename_or_file, *args, **kwargs)
    except TypeError:
        yield filename_or_file
    else:
        with file:
            yield file
