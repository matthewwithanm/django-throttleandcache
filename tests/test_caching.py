from django.core.cache import cache as cache_obj
from mock import Mock
from throttleandcache import cache


SOME_VALUE = {'hello': 'world'}


def teardown_function(fn):
    cache_obj.clear()


def test_none():
    fn = cache()(lambda: None)
    assert fn() is None


def test_caching():
    """
    Makes sure the cache is actually used.
    """
    f = Mock(__name__='f', return_value=None)
    decorated = cache()(f)
    decorated()
    decorated()
    assert f.call_count == 1


def test_value():
    """
    Makes sure the cached value is correct.
    """
    f = Mock(__name__='f', return_value=SOME_VALUE)
    decorated = cache()(f)
    assert decorated() == SOME_VALUE


def test_nocache():
    """
    Makes sure that the cache decorator doesn't cache when it has a 0
    timeout.
    """
    f = Mock(__name__='f', return_value=None)
    decorated = cache(timeout=0)(f)
    decorated()
    decorated()
    assert f.call_count == 2


def test_graceful():
    def f():
        if f.called:
            f.errored = True
            raise Exception
        f.called = True
        return SOME_VALUE

    f.called = False
    f.errored = False
    decorated = cache('0s', graceful=True)(f)
    decorated()  # Successful call
    value = decorated()  # Unsuccessful, but should be handled gracefully.
    assert f.errored
    assert value == SOME_VALUE


def test_change_timeout():
    f = Mock(__name__='f', return_value=SOME_VALUE)
    decorated = cache()(f)  # Cache FOREVER
    decorated()  # Warm cache
    f.return_value = None
    assert decorated() == SOME_VALUE
    assert cache(0)(f)() is None
