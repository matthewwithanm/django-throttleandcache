from hashlib import sha256
from django.core.cache import get_cache
from .settings import MAX_TIMEOUT


def __cache_key(fn, fn_args, fn_kwargs):
    key = fn.__module__ + fn.__name__ + repr(fn_args) + repr(fn_kwargs)
    return sha256(key).hexdigest()


class NoneResult:
    """
    Because the cache returns None when we try to retrieve a value for a key
    that doesn't exist, we need some way of representing None in the cache.
    This class is it.
    """
    pass


def cache_result(timeout=-1, cache='default', key_prefix=''):
    """
    Cache the result of a function call for <timeout> seconds.
    """
    cache_backend = get_cache(cache)
    
    if timeout == -1:
        timeout = MAX_TIMEOUT
    
    def decorator(fn):
        def wrapper(*args, **kwargs):
            key = key_prefix + __cache_key(fn, args, kwargs)
            cached_value = cache_backend.get(key)
            
            if cached_value is None:
                # The function call has not yet been cached.
                result = fn(*args, **kwargs)
                if result is None:
                    value_to_cache = NoneResult
                else:
                    value_to_cache = result
                cache_backend.set(key, value_to_cache, timeout)
            elif cached_value is NoneResult:
                result = None
            else:
                result = cached_value
            
            return result
        return wrapper
    return decorator
