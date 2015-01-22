Features
========

- Graceful handling of errors (can fall back to cached value)
- Calculate results in background (requires Celery_)
- Readable duration strings (`'1 day'` vs `86400`)
- Correct handling of `None`
- Per-call invalidation


Installation
============

1. `pip install django-throttleandcache`
2. Set a cache backend in your `settings.py` file.


Usage
=====

.. code-block:: python

    from throttleandcache import cache

    # Cache the result of my_function for 3 seconds.
    @cache('3s')
    def my_function():
        return 'whatever'

If you call the function multiple times *with the same arguments*, the result
will be fetched from the cache. In order to invalidate the cache for that call,
call `my_function.invalidate()` with the same arguments:

.. code-block:: python

    my_function()
    my_function() # Result pulled from cache
    my_function.invalidate()
    my_function() # Not from cache

If Celery_ is installed, you can remove the the calculation of new values from
the request/response cycle:

.. code-block:: python

    @cache('3s', background=True)
    def my_function():
        return 'whatever'

Note that, in the case of a cold cache, the value will still be calculated
synchronously. Stale values may be used while new ones are being calculated.

Remember that calling the same method on multiple instances means that each
invocation will have a different first positional (`self`) argument:

.. code-block:: python

    class A(object):
        @cache('100s')
        def my_function(self):
            print 'The method is being executed!'

    instance_1 = A()
    instance_2 = A()
    instance_1.my_function() # The original method will be invoked
    instance_2.my_function() # Different "self" argument, so the method is invoked again.

If you wish to cache the result across all instances, use `@cacheforclass`.

The first argument to the `cache` decorator is the timeout and can be given as
a number (of seconds) or a string. Since strings contain units, they can make
your code much more readable. Some examples are `'2s'`, `'3m'`, `'3m 2s'`, and
`'3 minutes, 2 seconds'`.

The `cache` decorator also accepts the following (optional) keyword arguments:

- **using**: specifies which cache to use.
- **key_prefix**: A string to prefix your cache key with.
- **key_func**: A function for deriving the cache key. This function will be
    passed the ``fn``, ``*args``, and ``**kwargs``.
- **graceful**: This argument specifies how errors should be handled. If
    `graceful` is `True` and your function raises an error, throttleandcache
    will log the error and return the cached value. If no cached value exists,
    the original error is raised.
- **background**: Specifies that new values should be calculated in the
    background (using Celery_).


.. _Celery: http://www.celeryproject.org/
