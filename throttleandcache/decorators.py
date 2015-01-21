from hashlib import sha256
from datetime import datetime
from django.core.cache import get_cache
from django.utils.decorators import method_decorator
from django.conf import settings
from functools import wraps
from time import mktime
from .logging import logger
from .tdparse import parse


to_key = lambda *args: ''.join(map(str, args))
fn_key = lambda fn: fn.__module__ + fn.__name__


def default_key_func(fn, *fn_args, **fn_kwargs):
    key = to_key(fn_key(fn), repr(fn_args), repr(fn_kwargs))
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


def get_ttl(expiration_time, now):
    """
    Convert an expiration time into a TTL in seconds.
    """
    return int(mktime(expiration_time.timetuple()) - mktime(now.timetuple()))


def cache(timeout=-1, using=None, key_prefix='', graceful=False,
          key_func=default_key_func):
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
            unprefixed_key = key_func(fn, *args, **kwargs)

            if unprefixed_key is None:
                return fn(*args, **kwargs)

            key = key_prefix + unprefixed_key
            cached = cache_backend.get(key)
            now = datetime.now()

            if cached:
                expiration_time = cached.set_time + expires_in

                if expiration_time > now:
                    if expiration_time != cached.expiration_time:
                        # Update the expiration time.
                        cached.expiration_time = expiration_time
                        cache_backend.set(key, cached, get_ttl(expiration_time))
                    return cached.value

            # The cached value is expired or the result was never cached. We
            # need to generate a new value.
            try:
                result = fn(*args, **kwargs)
            except Exception as exc:
                if graceful and cached:
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
                ttl = settings.THROTTLEANDCACHE_MAX_TIMEOUT
            else:
                ttl = get_ttl(then, now)
            val = CachedValue(result, now, then)
            cache_backend.set(key, val, ttl)

            return result

        def invalidate(*args, **kwargs):
            unprefixed_key = key_func(fn, *args, **kwargs)

            if unprefixed_key is None:
                return

            key = '%s%s' % (key_prefix, unprefixed_key)

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
