from django.core.cache import cache as cache_obj
from mock import Mock
from throttleandcache import cache


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
    f = Mock(__name__='f', return_value='hello world')
    decorated = cache()(f)
    assert decorated() == 'hello world'


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
