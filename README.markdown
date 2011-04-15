Setup
============

1. Set a cache backend in your `settings.py` file.
2. Add 'throttleandcache' to your `INSTALLED_APPS`


Usage
=====

    from throttleandcache.decorators import cache_result
    
    # Cache the result of my_function for 3 seconds.
    @cache_result(3)
    def my_function():
        return 'whatever'
