from __future__ import absolute_import
import logging


try:
    from logging import NullHandler
except ImportError:
    from logging import Handler

    class NullHandler(Handler):
        def emit(self, record):
            pass


logger = logging.getLogger('throttleandcache')
logger.addHandler(NullHandler())
