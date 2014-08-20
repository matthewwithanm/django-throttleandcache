from hashlib import sha256
from datetime import datetime
from django.core.cache import get_cache
from django.utils.decorators import method_decorator
from django.conf import settings
from functools import wraps
from time import mktime
from .logging import logger
from .tdparse import parse


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


def cache(timeout=-1, using=None, key_prefix='', graceful=False):
    """
    Cache the result of a function call for <timeout> seconds.
    """

    cache_backend = get_cache(using or settings.THROTTLEANDCACHE_DEFAULT_CACHE)

    if timeout == -1:
        timeout = settings.THROTTLEANDCACHE_MAX_TIMEOUT

    expires_in = parse(timeout)

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            key = key_prefix + __cache_key(fn, args, kwargs)
            cached = cache_backend.get(key)
            now = datetime.now()

            if cached:
                expiration_time = cached.set_time + expires_in
                expiration_time_changed = expiration_time != cached.expiration_time

            if not cached or expiration_time < now or expiration_time_changed:
                # The cached value is expired, the result was never cached, or
                # the expiration time has changed. We need to generate a new
                # value.
                try:
                    result = fn(*args, **kwargs)
                except Exception as exc:
                    if graceful and cached and not expiration_time_changed:
                        # There was an error executing the function, but we have
                        # a cached value to fall back to. Log the error and
                        # return the cached value.

                        logger.exception(exc)
                        return cached.value
                    raise

                then = now + expires_in
                if graceful:
                    # With the graceful option, we actually want to keep the
                    # result in the cache until we explicitly override it, in
                    # case we need it later. The expiration_time will be used
                    # to determine whether the value should be recalculated
                    # instead of its absence in the cache.
                    secs = settings.THROTTLEANDCACHE_MAX_TIMEOUT
                else:
                    secs = int(mktime(then.timetuple()) - mktime(now.timetuple()))
                val = CachedValue(result, now, then)
                cache_backend.set(key, val, secs)
            else:
                result = cached.value

            return result

        def invalidate(*args, **kwargs):
            key = key_prefix + __cache_key(fn, args, kwargs)

            if graceful:
                # Update the CachedValue's expiration time. This allows
                # subsequent calls to still fall back to the cached value if
                # there's an error.
                val = cache_backend.get(key)
                val.expiration_time = -1
                cache_backend.set(key, val, settings.THROTTLEANDCACHE_MAX_TIMEOUT)
            else:
                cache_backend.delete(key)

        wrapper.invalidate = invalidate

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
