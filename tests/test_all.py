from django.core.cache import cache
from mock import Mock
from throttleandcache.decorators import cache_result


def teardown_function(fn):
    cache.clear()


def test_none():
    fn = cache_result()(lambda: None)
    assert fn() is None


def test_caching():
    """
    Makes sure the cache is actually used.
    """
    f = Mock(__name__='f', return_value=None)
    decorated = cache_result()(f)
    decorated()
    decorated()
    assert f.call_count == 1


def test_value():
    """
    Makes sure the cached value is correct.
    """
    f = Mock(__name__='f', return_value='hello world')
    decorated = cache_result()(f)
    assert decorated() == 'hello world'


def test_nocache():
    """
    Makes sure that the cache decorator doesn't cache when it has a 0
    timeout.
    """
    f = Mock(__name__='f', return_value=None)
    decorated = cache_result(timeout=0)(f)
    decorated()
    decorated()
    assert f.call_count == 2
