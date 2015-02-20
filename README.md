automain
========

A library to automatically generate and run simple argparse parsers from function signatures.

## Tutorial

### Basic

Autocommand turns a function into a command-line program. It converts the function's parameter signature into command-line arguments, and automatically runs the function if the module was called as `__main__`. In effect, it lets your create a smart main function.

```python
from autocommand import automain

# This program takes exactly one argument and echos it.
@automain(__name__)
def echo(thing)
    print(thing)
```
```sh
$ python echo.py hello
hello
$ python echo.py -h
usage: echo [-h] thing

positional arguments:
  thing

optional arguments:
  -h, --help  show this help message and exit
$ python echo.py hello world  # too many arguments
usage: echo.py [-h] thing
echo.py: error: unrecognized arguments: world
```

As you can see, automain uses argparse to convert the signature of the function into an argument spec, which automatically handles creating a usage statement and argument parsing.

`automain` is passed `__name__` to allow it to automatically run the decorated function. If `__name__ == '__main__'`, the arguments are parsed and the function is executed. The program's return code is taken from the return value of the function, via `sys.exit`.

### Types

You can use a type annotation to give an argument a type. Any type (or in fact any callable) that returns an object when given a string argument can be used, though there are a few special cases that are described later. Keep in mind that `argparse` will catch `TypeErrors` raised during parsing, so you can supply a callable and do some basic argument validation as well.

```python
@automain(__name__)
def net_client(host, port: int):
    ...
```

### Options

To create `--option` switches, just assign a default. Automain will automatically create `--long` and `-s`hort switches.

```python
@automain(__name__)
def do_with_config(argument, config='~/foo.conf'):
    pass
```
```sh
$ python example.py -h
usage: example.py [-h] [-c CONFIG] argument

positional arguments:
  argument

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
```

The option's type is automatically deduced from the default, unless one is explicitly given in an annotation:

```python
@automain(__name__)
def http_connect(host, port=80):
    print('{}:{}'.format(host, port))
```
```sh
$ python http.py -h
usage: http.py [-h] [-p PORT] host

positional arguments:
  host

optional arguments:
  -h, --help            show this help message and exit
  -p PORT, --port PORT
$ python http.py localhost
localhost:80
$ python http.py localhost -p 8080
localhost:8080
$ python http.py localhost -p blah
usage: http.py [-h] [-p PORT] host
echo.py: error: argument -p/--port: invalid int value: 'blah'
```

#### Switches
If an argument is given a default value of `True` or `False`, or given an explicit `bool` type, it becomes an option switch.

```python
@automain(__name__)
def example(verbose=False, quiet=False):
    pass
```
```sh
$ python example.py -h
usage: example.py [-h] [-v] [-q]

optional arguments:
  -h, --help     show this help message and exit
  -v, --verbose
  -q, --quiet
```

Automain attempts to do the "correct thing" in these cases- if the default is `True`, then supplying the switch makes the argument `False`; if the type is `bool` and the default is some other `True` value, then supplying the switch makes the argument `False`, while not supplying the switch makes the argument the default value.

#### Files

If the default value is a file object, such as `sys.stdout`, then automain just looks for a string, for a file path. It doesn't do any special checking on the string, though (such as checking if the file exists)- it's better to let the client decide how to handle errors in this case. Instead, it provides a special context manager called `smart_open`, which behaves exactly like `open` if a filename or other openable type is provided, but also lets you use already open files:

```python
from autocommand import automain, smart_open
import sys

# Write the contents of stdin, or a file, to stdout
@automain(__name__)
def write_to(infile=sys.stdin):
    with smart_open(infile) as f:
        for line in f:
            print(line.rstrip())
    # If a file was opened, it is closed here. If it was just stdin, it is untouched.
```
``` sh
$ echo "Hello World!" | python write_to.py | tee hello.txt
Hello World!
$ python write_to.py --infile hello.txt
Hello World!
```

### Descriptions and docstrings

The `automain` decorator accepts `description` and `epilog` kwargs, corresponding to the [`description`](https://docs.python.org/3/library/argparse.html#description) and [`epilog`](https://docs.python.org/3/library/argparse.html#epilog) of the `ArgumentParser`. If no description is given, but the decorated function has a  docstring, then it is taken as the `description` for the `ArgumentParser`

```python
@automain(__name__, epilog='Some extra documentation in the epilog')
def copy(infile=sys.stdin, outfile=sys.stdout):
    '''
    Copy an the contents of a file (or stdin) to another file (or stdout)
    '''
    with smart_open(infile) as istr:
        with smart_open(outfile, 'w') as ostr:
            for line in istr:
                ostr.write(line)
```
```sh
$ python copy.py -h
usage: .\echo.py [-h] [-i INFILE] [-o OUTFILE]

Copy an the contents of a file (or stdin) to another file (or stdout)

optional arguments:
  -h, --help            show this help message and exit
  -i INFILE, --infile INFILE
  -o OUTFILE, --outfile OUTFILE

Some extra documentation in the epilog
$ echo "Hello World" | python copy.py --outfile hello.txt
$ python copy.py --infile hello.txt --outfile hello2.txt
$ python copy.py --infile hello2.txt
Hello World
```

### Parameter descriptions

You can also attach description text to individual parameters in the annotation. To attach both a type and a description, supply them both in any order in a tuple

```python
@automain(__name__)
def copy_net(
    infile: 'The name of the file to send',
    host: 'The host to send the file to',
    port: (int, 'The port to connect to'))

    '''
    Copy a file over raw TCP to a remote destination.
    '''
    # Left as an exercise to the reader
```

### Testing and Library use

The decorated function is only called and exited from if the first argument to `automain` is `'__main__'`. If no argument is given, or it is not main, then a new main wrapper function is created by the decorator. This function has the signature `*argv`, and is intended to be called with arguments as from `sys.argv`. The function has the attributes `parser` and `main`, which are the generated `ArgumentParser` and the original main function that was decorated. This is to facilitate testing and library use of your main. Calling the function triggers a `parse_args()` with the supplied arguments, and returns the result of the main function. Note that, while it returns instead of calling `sys.exit`, the `parse_args()` function will raise a `SystemExit` in the event of a parsing error or `-h/--help` argument.

```python
@automain()
def test_prog(arg1, arg2: int, quiet=False, verbose=False):
    if not quiet:
        print(arg1, arg2)
        if verbose:
            print("LOUD NOISES")
    
    return 0

# Note that argv[0] must be included.
print(test_prog('test', '-v', 'hello', '80'))
```
```
hello 80
LOUD NOISES
0
```

### Features, notes, and limitations

- `--options` are given single character `-s`hort options as well, if possible. Each capitalization of the first letter in the parameter name is tried. If any parameters have only a single letter name, they aren't given `--long` versions.
- `automain` supports a few other kwargs:
    - If a `parser` is given, that parser object is used instead of one being generated on from the function signature. This allows you to use a more elaborate parser, with features that aren't supported by the automation system in `automain`.
    - If `add_nos` is set to True, then for each boolean `--switch` in the parameter list, a `--no-switch` is added, to cancel it out.
- If the decorated function has a `*args`, then 0 or more arguments are collected into a list. No default value can be given, but a type and/or description annotation may.
- There are a few possible exceptions that `automain` can raise. All of them derive from `autocommand.AutocommandError`, which is a `TypeError`.
    - If an invalid annotation is given (that is, it isn't a `type`, `str`, `(type, str)`, or `(str, type)`, an `AnnotationError` is raised
    - If the function has a `**kwargs` parameter, a `KWargError` is raised.
    - If, somehow, the function has a positional-only parameter, a `PositionalArgError` is raised. This means that the argument doesn't have a name, which is currently not possible with a plain `def` or `lambda`, though many built-in functions have this kind of parameter.
- There are a few argparse features that are not supported by autocommand.
    - It isn't possible to have an optional positional argument (as opposed to a `--option`). POSIX and GNU think this is bad form anyway.
    - It isn't possible to have mutually exclusive arguments or options
    - It isn't possible to have subcommands or subparsers, though I'm working on a few solutions involving classes or nested function definitions to allow this.
