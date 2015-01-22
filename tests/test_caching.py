from django.core.cache import cache as cache_obj
from mock import Mock, patch
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


def test_invalidate():
    """
    Ensure that invalidate clears the cache.
    """
    f = Mock(__name__='f', return_value=None)
    decorated = cache()(f)
    decorated()
    decorated.invalidate()
    decorated()
    assert f.call_count == 2


def test_invalidate_args():
    """
    Ensure that invalidate clears the cache for the provided args.
    """
    f = Mock(__name__='f', return_value=None)
    decorated = cache()(f)
    decorated(1)
    decorated.invalidate(1)
    decorated(1)
    assert f.call_count == 2


def test_only_invalidate_args():
    """
    Ensure that invalidate doesn't clear the cache for other args.
    """
    f = Mock(__name__='f', return_value=None)
    decorated = cache()(f)
    decorated(1)
    decorated.invalidate(2)
    decorated(1)
    assert f.call_count == 1


def test_key_func():
    """
    Test that the provided key function is used.
    """
    f = Mock(__name__='f', return_value=None)
    g = Mock(__name__='g', return_value=None)
    key_func = lambda fn, *args, **kwargs: 'key'
    cache(key_func=key_func)(f)()
    cache(key_func=key_func)(g)()
    assert g.call_count == 0


def test_key_func_nocache():
    """
    Test that returning ``None`` from the key function bypasses the cache.
    """
    f = Mock(__name__='f', return_value=None)
    key_func = lambda fn, *args, **kwargs: None
    decorated = cache(key_func=key_func)(f)
    decorated(1)
    decorated(1)
    assert f.call_count == 2


def test_background():
    """
    Test that caching in the background will actually call the celery task.
    """
    f = Mock(__name__='f', return_value=SOME_VALUE)
    with patch('throttleandcache.decorators._get_result.delay') as mocked:
        # Use a zero timeout to make sure that the value is expired for
        # subsequent calls.
        decorated = cache(timeout=0, background=True)(f)

        # With a cold cache, the call should be synchronous.
        decorated()
        assert f.call_count == 1
        assert mocked.call_count == 0

        # After that, the Celery task should be used.
        decorated()
        assert f.call_count == 1
        assert mocked.call_count == 1
