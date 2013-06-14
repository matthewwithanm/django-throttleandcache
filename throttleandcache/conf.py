from appconf import AppConf
from django.conf import settings


class ThrottleAndCacheConf(AppConf):
    MAX_TIMEOUT = 60 * 60 * 24 * 365 * 10
