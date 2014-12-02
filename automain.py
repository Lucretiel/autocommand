# Copyright 2014-2015 Nathan West
#
# This file is part of automain.
#
# automain is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# automain is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with automain.  If not, see <http://www.gnu.org/licenses/>.
#

from inspect import signature, Parameter
from argparse import ArgumentParser
from contextlib import contextmanager, ExitStack
from io import IOBase


_empty = Parameter.empty


class _Autofile:
    '''
    Base class for the autofile feature. Should be instantiated with the future
    arguments to open(). See the `autofile` function for a system to create
    _Autofile subclasses with pre-defined args and kwargs for open(), which can
    be instantiated with a filename.

    This is a class, and not a function, to make it easy to detect as a main
    function annotation.
    '''
    def __init__(self, handler, *open_args, **open_kwargs):
        '''
        Initialize the Autofile.
        `open_args`: the arguments to the open(...) call
        `open_kwargs`: the kwargs to the open(...) call
        `handler`: An optional error handler. If an exception is raised opening
            the file, it is passed to this function, and the return value sent
            to the context instead of a file object.
        '''
        self.handler = handler
        self.args = open_args
        self.kwargs = open_kwargs

    @contextmanager
    def open(self):
        try:
            # Can't just yield open(...) because an exception could be raised
            # from the context.
            f = open(*self.args, **self.kwargs)
        except OSError as e:
            # Can't just call and catch TypeError, because handler may raise.
            if callable(self.handler):
                yield self.handler(e)
            else:
                raise
        else:
            with f:
                yield f


def autofile(*args, handler=None, **kwargs):
    '''
    Create an autofile type. When used by automain, autofiles are automatically
    opened before main is called. The opened file objects are passed as
    arguments, and automatically closed when main returns, even if it throws an
    exception.

    The optional handler argument allows you define an error-handler function.
    If given, and an exception is raised trying to open the file, the function
    is called with the exception, and the return value is passed to the main
    function, instead of a file object. If no handler is given, the exception
    is simply raised back to the main caller.

    Of course, because the objects passed to main as arguments are normal file
    objects, you can use your own "with" context to close the file earlier, as
    consecutive close() calls are safe no-ops. Just be careful not to close
    a standard stream if you provide it as a default argument.

    Example:

        @automain(__name__):
        def main(
            input_file: ("The file to read from", autofile('r')) =stdin,
            output_file: ("The file to write to", autofile('w')) =stdout):

            ...

    '''
    class ScopedAutofile(_Autofile):
        def __init__(self, filename):
            super().__init__(handler, filename, *args, **kwargs)
    return ScopedAutofile


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

    raise ValueError(
        'parameter annotation must be type, description, or tuple of both',
        annotation)


def _add_argument(param, used_char_args):
    '''
    Get the *args and **kwargs to use for parser.add_argument for a given
    parameter.
    '''
    if param.kind is param.POSITIONAL_ONLY:
        raise ValueError("parameter must have a name", param)
    elif param.kind is param.VAR_KEYWORD:
        raise ValueError("automain doesn't understand kwargs", param)

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

    # Add the type
    if arg_type is not None:
        # Special case for bool: make it just a --switch
        if arg_type is bool:
            if not default or default is _empty:
                arg_spec['action'] = 'store_true'
            else:
                arg_spec['action'] = 'store_false'

            # Make it an option even if there's no explicit default
            is_option = True
            # TODO: Update bool to support --no-option, as a counter to --option

        # Special case for file object types: make it a string type, for filename
        elif issubclass(arg_type, IOBase):
            arg_spec['type'] = str

        # TODO: special case for list type.
        #   - How to specificy type of list members?
        #   - action='append' vs nargs='*'

        # Everything else: make it a plain type
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

    # Add default. The presence of a default means this is an option, not an
    # argument.
    if default is not _empty:
        arg_spec['default'] = default
        is_option = True

    # Get the --flags
    flags = []
    name = param.name

    if is_option:
        # Add the first letter as a -short option. Attempt to add -c or -C,
        # trying various capitalizations.
        for letter in name[0], name[0].upper(), name[0].lower():
            if letter not in used_char_args:
                used_char_args.add(letter)
                flags.append('-{}'.format(letter))
                break

        # If the function argument only had one letter, and it could be added
        # as a -short option, don't bother adding a --long option
        if not (len(name) == 1 and flags):
            flags.append('--{}'.format(name))

        # Add an explicit dest, in case the name was converted
        arg_spec['dest'] = name
    else:
        flags.append(name)

    return flags, arg_spec


def automain(module=None, description=None, epilog=None):
    '''
    Decorator to create an automain function. The function's signature is
    analyzed, and an ArgumentParser is created, using the `description` and
    `epilog` parameters, to parse command line arguments corrosponding to the
    function's parameters. The function's signature is changed to accept a
    single argv parameter, as from sys.argv, though you can supply your own.
    When called, the function parses the arguments provided, then supplies them
    to the decorated function. Keep in mind that this happens with plain
    argparse, so supplying invalid arguments or '-h' will cause a usage
    statement to be printed and a SystemExit to be raised.

    Optionally, pass a module name (typically __name__) as the first argument
    to `automain`. If you do, and it is "__main__", the decorated function is
    called immediately with sys.argv, and the progam is exited with the return
    value; this is so that you can call @automain(__name__) and still be able
    to import the module for testing.

    The decorated function is attached to the result as the `main` attribute.
    '''
    def decorator(main):
        parser = ArgumentParser(description=description, epilog=epilog)
        main_sig = signature(main)

        used_char_args = {'h'}
        # Add each argument. Do single-character arguments first, if present,
        # so that they get priority, and don't have to get --long versions.
        # sorted is stable, so the parameters will still be in relative order.
        for param in sorted(main_sig.parameters.values(),
                key=lambda param: len(param.name) > 1):
            flags, spec = _add_argument(param, used_char_args)
            parser.add_argument(*flags, **spec)

        # No functools.wraps, because the signature and functionality is so
        # different
        def main_wrapper(argv):
            # Update parser with program name
            parser.prog = argv[0]

            # Parse arguments
            args = vars(parser.parse_args(argv[1:]))

            # Get empty argument binding
            function_args = main_sig.bind_partial()

            # Context for autofiles
            with ExitStack() as stack:
                # Open autofiles
                for arg_name, arg_value in args.items():
                    if isinstance(arg_value, _Autofile):
                        args[arg_name] = stack.enter_context(arg_value.open())

                # TODO: do something smarter if the file can't be opened

                # Apply command line arguments to function arguments
                function_args.arguments.update(args)

                # Call main function
                return main(*function_args.args, **function_args.kwargs)

        # If we are running as a script/program, call main right away, then exit
        if module == '__main__':
            from sys import exit as sys_exit, argv as sys_argv
            sys_exit(main_wrapper(sys_argv))

        # Otherwise, attach the wrapped main function, and return the wrapper.
        main_wrapper.main = main
        return main_wrapper

    return decorator


@contextmanager
def smart_open(filename_or_file, *args, **kwargs):
    '''
    This context manager allows you to correctly open a filename, if you want
    to default some already-existing file object, like sys.stdout, which
    shouldn't be closed at the end of the context. If the filename argument is
    a str, bytes, or int, the file object is created via a call to open with
    the given *args and **kwargs, sent to the context, and closed at the end of
    the context, just like "with open(filename) as f". If it isn't one of the
    openable types, the object simply sent to the context unchanged. Example:

        def work_with_file(name=sys.stdout):
            with smart_open(name) as f:
                # Works correctly if name is a str filename or sys.stdout
                print("Some stuff", file=f)
                # If it was a filename, f is closed at the end here.
    '''
    if isinstance(filename_or_file, (str, bytes, int)):
        with open(filename_or_file, *args, **kwargs) as f:
            yield f
    else:
        yield filename_or_file

