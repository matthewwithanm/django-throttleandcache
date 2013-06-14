from appconf import AppConf
from django.conf import settings


class ThrottleAndCacheConf(AppConf):
    DEFAULT_CACHE = None
    MAX_TIMEOUT = 60 * 60 * 24 * 365 * 10

    def configure_default_cache(self, value):
        if value is None:
            try:
                from django.core.cache.backends.dummy import DummyCache
            except ImportError:
                dummy_cache = 'dummy://'
            else:
                dummy_cache = 'django.core.cache.backends.dummy.DummyCache'

            # DEFAULT_CACHE_ALIAS doesn't exist in Django<=1.2
            try:
                from django.core.cache import DEFAULT_CACHE_ALIAS as default_cache_alias
            except ImportError:
                default_cache_alias = 'default'

            if settings.DEBUG:
                value = dummy_cache
            elif default_cache_alias in getattr(settings, 'CACHES', {}):
                value = default_cache_alias
            else:
                value = getattr(settings, 'CACHE_BACKEND', None) or dummy_cache

        return value
