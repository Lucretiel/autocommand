import pytest
import asyncio
from contextlib import closing, contextmanager
from autocommand.autoasync import autoasync


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
        with temporary_context_loop(new_loop) as loop:
            yield loop


def test_basic_autoasync(context_loop):
    data = []

    @asyncio.coroutine
    def coro_1():
        data.append(1)
        yield
        data.append(3)

        return 1

    @asyncio.coroutine
    def coro_2():
        data.append(2)
        yield
        data.append(4)

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
    assert data == [1, 2, 3, 4]


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


def test_run_forever(context_loop):
    @asyncio.coroutine
    def stop_loop_after_1_tenth_second():
        yield from asyncio.sleep(0.1)
        context_loop.stop()

    retrieved_value = False

    @asyncio.coroutine
    def set_value_after_half_tenth_second():
        nonlocal retrieved_value
        yield from asyncio.sleep(0.05)
        retrieved_value = True

    @autoasync(forever=True)
    @asyncio.coroutine
    def async_main():
        asyncio.async(stop_loop_after_1_tenth_second())
        asyncio.async(set_value_after_half_tenth_second())
        yield
        return 10

    assert async_main() != 10  # Nothing should be returned
    assert retrieved_value


def test_defered_loop(context_loop, new_loop):
    '''
    Test that, if a new
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
