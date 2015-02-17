from django.conf import settings
from mock import Mock, patch
from throttleandcache.decorators import get_cache_backend
from throttleandcache import cache


def test_gh_1():
    """Test that updating the TTL doesn't break backgrounding."""
    cache_backend = get_cache_backend('default')
    mocked = Mock(wraps=cache_backend)
    with patch('throttleandcache.decorators.get_cache_backend') as factory:
        factory.return_value = mocked

        f = Mock(__name__='f', return_value=None)
        key_func = lambda *args, **kwargs: 'key'

        # Prime the cache
        decorated = cache('5s', key_func=key_func, graceful=True)(f)
        decorated()

        ttl = mocked.set.call_args[0][2]
        assert ttl == settings.THROTTLEANDCACHE_MAX_TIMEOUT

        # Now change the cache TTL
        decorated = cache('6s', key_func=key_func, graceful=True)(f)
        decorated()

        ttl = mocked.set.call_args[0][2]
        assert ttl == settings.THROTTLEANDCACHE_MAX_TIMEOUT
