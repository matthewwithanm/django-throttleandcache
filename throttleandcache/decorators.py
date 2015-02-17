from hashlib import sha256
from datetime import datetime
from django.core.cache import get_cache
from django.utils.decorators import method_decorator
from django.conf import settings
from functools import wraps
from time import mktime
from .logging import logger
from .tdparse import parse


__all__ = ['cache', 'cacheforclass', 'cacheforinstance', 'cache_result']


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


def get_ttl(expiration_time, now, keep_expired=False):
    """
    Convert an expiration time into a TTL in seconds.
    """
    if keep_expired:
        # With the graceful and background options, we actually want to keep
        # the result in the cache until we explicitly override it, in case we
        # need it later. The expiration_time will be used to determine whether
        # the value should be recalculated instead of its absence in the cache.
        return settings.THROTTLEANDCACHE_MAX_TIMEOUT

    return int(mktime(expiration_time.timetuple()) - mktime(now.timetuple()))


def get_cache_backend(name=None):
    return get_cache(name or settings.THROTTLEANDCACHE_DEFAULT_CACHE)


def get_result(key, fn, args, kwargs, timeout, cache_name, graceful,
               background, keep_expired=None):
    """
    Get the result of the provided operation. The function will not actually be
    called if an unexpired value can be found in the cache.
    """

    # A key of `None` tells us not to use the cache.
    if key is None:
        return fn(*args, **kwargs)

    if timeout == -1:
        timeout = settings.THROTTLEANDCACHE_MAX_TIMEOUT

    keep_expired = (graceful or background if keep_expired is None
                    else keep_expired)
    expires_in = parse(timeout)
    cache_backend = get_cache_backend(cache_name)
    cached = cache_backend.get(key)
    now = datetime.now()

    if cached:
        expiration_time = cached.set_time + expires_in

        if expiration_time > now:
            if expiration_time != cached.expiration_time:
                # Update the expiration time.
                cached.expiration_time = expiration_time
                cache_backend.set(key, cached,
                                  get_ttl(expiration_time, now, keep_expired))
            return cached.value

        # The cached value is expired, but we'll use it anyway and get
        # a new value in a background process.
        if background:
            # Try importing Celery. This way, trying to use ``background=True``
            # without installing Celery will give an error that clues you in to
            # the reason.
            from celery import task  # noqa
            _get_result.delay(key=key, fn=fn, args=args, kwargs=kwargs,
                              timeout=timeout, cache_name=cache_name,
                              graceful=False, background=False,
                              keep_expired=True)
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
    ttl = get_ttl(then, now, keep_expired)
    val = CachedValue(result, now, then)
    cache_backend.set(key, val, ttl)

    return result


try:
    from celery import task
except ImportError:
    pass
else:
    _get_result = task(ignore_result=True, serializer='pickle')(get_result)


def get_key(prefix, key_func, fn, args, kwargs):
    unprefixed_key = key_func(fn, *args, **kwargs)
    return '%s%s' % (prefix, unprefixed_key) if unprefixed_key else None


def cache(timeout=-1, using=None, key_prefix='', graceful=False,
          key_func=default_key_func, background=False):
    """
    Cache the result of a function call for <timeout> seconds.
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            key = get_key(key_prefix, key_func, fn, args, kwargs)
            return get_result(key=key, fn=fn, args=args, kwargs=kwargs,
                              timeout=timeout, cache_name=using,
                              graceful=graceful, background=background)

        def invalidate(*args, **kwargs):
            key = get_key(key_prefix, key_func, fn, args, kwargs)

            if key is None:
                return

            cache_backend = get_cache_backend(using)
            keep_expired = graceful or background

            if keep_expired:
                # Update the CachedValue's expiration time. This allows
                # subsequent calls to still fall back to the cached value if
                # there's an error.
                cached = cache_backend.get(key)
                if cached:
                    cached.expiration_time = -1
                    cache_backend.set(key, cached,
                                      settings.THROTTLEANDCACHE_MAX_TIMEOUT)
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
