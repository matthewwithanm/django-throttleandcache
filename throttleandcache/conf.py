from appconf import AppConf
from django.conf import settings


def get_dummy_cache():
    try:
        from django.core.cache.backends.dummy import DummyCache  # noqa
    except ImportError:
        return 'dummy://'
    else:
        return 'django.core.cache.backends.dummy.DummyCache'


def get_default_cache_alias():
    # DEFAULT_CACHE_ALIAS doesn't exist in Django<=1.2
    try:
        from django.core.cache import DEFAULT_CACHE_ALIAS
        return DEFAULT_CACHE_ALIAS
    except ImportError:
        return 'default'


class ThrottleAndCacheConf(AppConf):
    DEFAULT_CACHE = None
    MAX_TIMEOUT = 60 * 60 * 24 * 365 * 10

    def configure_default_cache(self, value):
        if value is not None:
            return value

        if settings.DEBUG:
            return get_dummy_cache()

        default_cache_alias = get_default_cache_alias()
        if default_cache_alias in getattr(settings, 'CACHES', {}):
            return default_cache_alias

        return getattr(settings, 'CACHE_BACKEND', None) or get_dummy_cache()
