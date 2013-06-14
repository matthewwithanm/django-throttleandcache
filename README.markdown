Installation
============

1. `pip install -e git+git://github.com/matthewwithanm/django-throttleandcache.git#egg=django-throttleandcache`
2. Set a cache backend in your `settings.py` file.


Usage
=====

    from throttleandcache.decorators import cache

    # Cache the result of my_function for 3 seconds.
    @cache(3)
    def my_function():
        return 'whatever'

If you call the function multiple times *with the same arguments*, the result
will be fetched from the cache. Remember that calling the same method on
multiple instances means that each invocation will have a different first
positional (`self`) argument:

    class A(object):
        @cache(100)
        def my_function(self):
            print 'The method is being executed!'

    instance_1 = A()
    instance_2 = A()
    instance_1.my_function() # The original method will be invoked
    instance_2.my_function() # Different "self" argument, so the method is invoked again.

If you wish to cache the result across all instances, make sure the method will
be called with the same arguments (by making it a static or class method, removing it
from the class altogether, or using a utility like
`django.utils.decorators.method_decorator`).

The `cache` decorator also accepts optional `using` and `key_prefix` keyword arguments.
