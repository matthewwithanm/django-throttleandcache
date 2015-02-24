from celery import task
from .decorators import get_result

_get_result = task(ignore_result=True, serializer='pickle')(get_result)
