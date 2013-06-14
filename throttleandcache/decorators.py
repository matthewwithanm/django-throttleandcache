from hashlib import sha256
from datetime import datetime, timedelta
from django.core.cache import get_cache
from django.utils.decorators import method_decorator
from django.conf import settings
from functools import wraps


def __cache_key(fn, fn_args, fn_kwargs):
    key = fn.__module__ + fn.__name__ + repr(fn_args) + repr(fn_kwargs)
    return sha256(key).hexdigest()


class CachedValue(object):
    """
    A wrapper for cached values. This allows us to store ``None``, as well as
    letting us store metadata along with the result in the cache.

    """
    def __init__(self, value, set_time, expiration_time):
        self.value = value
        self.set_time = set_time
        self.expiration_time = expiration_time


def cache(timeout=-1, using=None, key_prefix=''):
    """
    Cache the result of a function call for <timeout> seconds.
    """

    cache_name = using
    if cache_name is None:
        # Fall back to CACHE_BACKEND for old versions of django.
        cache_name = getattr(settings, 'CACHE_BACKEND', 'default')

    cache_backend = get_cache(cache_name)

    if timeout == -1:
        timeout = settings.THROTTLEANDCACHE_MAX_TIMEOUT

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            key = key_prefix + __cache_key(fn, args, kwargs)
            cached = cache_backend.get(key)

            if cached is None:
                # The function call has not yet been cached.
                result = fn(*args, **kwargs)
                val = CachedValue(result, datetime.now(),
                                  datetime.now() + timedelta(seconds=timeout))
                cache_backend.set(key, val, timeout)
            else:
                result = cached.value

            return result
        return wrapper
    return decorator


# Aliases for clarity
cacheforinstance = cache


def cacheforclass(*args, **kwargs):
    decorator = cache(*args, **kwargs)
    return method_decorator(decorator)


# For backwards compatibility
def cache_result(timeout=-1, cache=None, key_prefix=''):
    return cache(timeout, cache, key_prefix)
