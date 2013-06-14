Features
========

- Graceful handling of errors (can fall back to cached value)
- Readable duration strings (`'1 day'` vs `86400`)
- Correct handling of `None`


Installation
============

1. `pip install django-throttleandcache`
2. Set a cache backend in your `settings.py` file.


Usage
=====

    from throttleandcache import cache

    # Cache the result of my_function for 3 seconds.
    @cache('3s')
    def my_function():
        return 'whatever'

If you call the function multiple times *with the same arguments*, the result
will be fetched from the cache. Remember that calling the same method on
multiple instances means that each invocation will have a different first
positional (`self`) argument:

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
- **graceful**: This argument specifies how errors should be handled. If
    `graceful` is `True` and your function raises an error, throttleandcache
    will log the error and return the cached value. If no cached value exists,
    the original error is raised.
