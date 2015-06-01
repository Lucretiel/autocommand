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

from asyncio import get_event_loop, coroutine
from functools import wraps


def autoasync(coro=None, *, loop=None, forever=False, pass_loop=False):
    '''
    Convert an asyncio coroutine into a function which, when called, is
    evaluted in an event loop, and the return value returned. This is intented
    to make it easy to write entry points into asyncio coroutines, which
    otherwise need to be explictly evaluted with an event loop's
    run_until_complete. This decorator internally applies the @coroutine
    decorator to the decorated function.

    `loop` defaults to asyncio.get_event_loop(). The call is defered until the
    function itself is called, so that clients can install custom event loops
    or event loop policies.

    If `forever` is True, the loop is run forever after the decorated coroutine
    is finished.

    If `pass_loop` is True, the event loop object is passed into the coroutine
    as the `loop` kwarg when the wrapper function is called.

    This coroutine can be called with ( @autoasync(...) ) or without
    ( @autoasync ) arguments.

    Examples:

    @autoasync
    def get_file(host, port):
        reader, writer = yield from asyncio.open_connection(host, port)
        data = reader.read()
        sys.stdout.write(data.decode())

    get_file(host, port)

    @autoasync(forever=True, pass_loop=True)
    def server(host, port, loop):
        yield_from loop.create_server(Proto, host, port)

    server('localhost', 8899)

    '''
    if coro is None:
        return lambda c: autoasync(
            c, loop=loop,
            forever=forever,
            pass_loop=pass_loop)

    coro = coroutine(coro)

    @wraps(coro)
    def autoasync_wrapper(*args, **kwargs):
        # Defer the call to get_event_loop so that, if a custom policy is
        # installed, it is respected at call time.
        local_loop = loop or get_event_loop()

        if pass_loop:
            kwargs['loop'] = local_loop

        if forever:
            local_loop.create_task(coro(*args, **kwargs))
            local_loop.run_forever()
        else:
            return local_loop.run_until_complete(coro(*args, **kwargs))

    return autoasync_wrapper
