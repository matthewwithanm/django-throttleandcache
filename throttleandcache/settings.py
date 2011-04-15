from django.conf import settings

MAX_TIMEOUT = getattr(settings, 'THROTTLEANDCACHE_MAX_TIMEOUT', 60 * 60 * 24 * 365 * 10)
