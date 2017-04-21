# Copyright 2014-2016 Nathan West
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

import pytest
from contextlib import closing, contextmanager
asyncio = pytest.importorskip('asyncio')
autoasync = pytest.importorskip('autocommand.autoasync').autoasync


@contextmanager
def temporary_context_loop(loop):
    '''
    Set the given loop as the context loop (that is, the loop returned by
    asyncio.get_event_loop() for the duration of the context)
    '''
    old_loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    try:
        yield loop
    finally:
        asyncio.set_event_loop(old_loop)


@pytest.yield_fixture
def new_loop():
    '''
    Get a new event loop. The loop is closed afterwards
    '''
    with closing(asyncio.new_event_loop()) as loop:
        yield loop


@pytest.yield_fixture
def context_loop():
    '''
    Create a new event loop and set it as the current context event loop.
    asyncio.get_event_loop() will return this loop within this fixture. Restore
    the original current event loop afterwards. The new loop is also closed
    afterwards.
    '''

    # Can't reuse new_loop() because some tests require new_loop and
    # context_loop to be different
    with closing(asyncio.new_event_loop()) as new_loop:
        with temporary_context_loop(new_loop):
            yield new_loop


def test_basic_autoasync(context_loop):
    data = set()

    @asyncio.coroutine
    def coro_1():
        data.add(1)
        yield
        data.add(2)

        return 1

    @asyncio.coroutine
    def coro_2():
        data.add(3)
        yield
        data.add(4)

        return 2

    @autoasync
    def async_main():
        task1 = asyncio.async(coro_1())
        task2 = asyncio.async(coro_2())

        result1 = yield from task1
        result2 = yield from task2

        assert result1 == 1
        assert result2 == 2

        return 3

    assert async_main() == 3
    assert data == {1, 2, 3, 4}


def test_custom_loop(context_loop, new_loop):
    did_bad_coro_run = False

    @asyncio.coroutine
    def bad_coro():
        nonlocal did_bad_coro_run
        did_bad_coro_run = True
        yield

    asyncio.async(bad_coro())

    @autoasync(loop=new_loop)
    @asyncio.coroutine
    def async_main():
        yield
        yield
        return 3

    assert async_main() == 3
    assert did_bad_coro_run is False


def test_pass_loop(context_loop):
    @autoasync(pass_loop=True)
    @asyncio.coroutine
    def async_main(loop):
        yield
        return loop

    assert async_main() is asyncio.get_event_loop()


def test_pass_loop_prior_argument(context_loop):
    '''
    Test that, if loop is the first positional argument, other arguments are
    still passed correctly
    '''
    @autoasync(pass_loop=True)
    @asyncio.coroutine
    def async_main(loop, argument):
        yield
        return loop, argument

    loop, value = async_main(10)
    assert loop is asyncio.get_event_loop()
    assert value == 10


def test_pass_loop_kwarg_only(context_loop):
    @autoasync(pass_loop=True)
    @asyncio.coroutine
    def async_main(*, loop, argument):
        yield
        return loop, argument

    loop, value = async_main(argument=10)
    assert loop is asyncio.get_event_loop()
    assert value == 10


def test_run_forever(context_loop):
    @asyncio.coroutine
    def stop_loop_after(t):
        yield from asyncio.sleep(t)
        context_loop.stop()

    retrieved_value = False

    @asyncio.coroutine
    def set_value_after(t):
        nonlocal retrieved_value
        yield from asyncio.sleep(t)
        retrieved_value = True

    @autoasync(forever=True)
    @asyncio.coroutine
    def async_main():
        asyncio.async(set_value_after(0.1))
        asyncio.async(stop_loop_after(0.2))
        yield

    async_main()
    assert retrieved_value


def test_run_forever_func(context_loop):
    @asyncio.coroutine
    def stop_loop_after(t):
        yield from asyncio.sleep(t)
        context_loop.stop()

    retrieved_value = False

    @asyncio.coroutine
    def set_value_after(t):
        nonlocal retrieved_value
        yield from asyncio.sleep(t)
        retrieved_value = True

    @autoasync(forever=True)
    def main_func():
        asyncio.async(set_value_after(0.1))
        asyncio.async(stop_loop_after(0.2))

    main_func()
    assert retrieved_value


def test_defered_loop(context_loop, new_loop):
    '''
    Test that, if a new event loop is installed with set_event_loop AFTER the
    autoasync decorator is applied (and no loop= is explicitly given to
    autoasync), the new event loop is used when the decorated function is
    called.
    '''
    @autoasync(pass_loop=True)
    @asyncio.coroutine
    def async_main(loop):
        yield
        return loop

    with temporary_context_loop(new_loop):
        passed_loop = async_main()
        assert passed_loop is new_loop
        assert passed_loop is asyncio.get_event_loop()
        assert passed_loop is not context_loop

    assert passed_loop is not asyncio.get_event_loop()
