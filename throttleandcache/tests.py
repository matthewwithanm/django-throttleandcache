from django.test import TestCase
from .decorators import cache_result


class CacheDecoratorTest(TestCase):
    
    def __init__(self, *args, **kwargs):
        self._call_counts = {
            '_uncached_fn': 0,
            '_test_caching_fn': 0,
        }
        super(CacheDecoratorTest, self).__init__(*args, **kwargs)

    @cache_result()
    def _return_none(self):
        return None
    
    @cache_result(0)
    def _uncached_fn(self):
        self._call_counts['_uncached_fn'] += 1
        return 1
        
    @cache_result()
    def _test_caching_fn(self):
        self._call_counts['_test_caching_fn'] += 1
        return 1
        
    @cache_result()
    def _test_value_fn(self):
        return 'any value'
    
    def test_none(self):
        self._return_none()
        self.assertTrue(self._return_none() is None, 'The expected value was not returned from the cache.')

    def test_caching(self):
        """
        Makes sure the cache is actually used.
        """
        self._test_caching_fn()
        self._test_caching_fn()
        self.assertEqual(self._call_counts['_test_caching_fn'], 1, 'The function was called when the cached value should have been used.')
    
    def test_value(self):
        """
        Makes sure the cached value is correct.
        """
        first_value = self._test_value_fn()
        self.assertEqual(first_value, self._test_value_fn(), 'The expected value was not returned from the cache.')

    def test_nocache(self):
        """
        Makes sure that the cache decorator doesn't cache when it has a 0
        timeout.
        """
        self._uncached_fn()
        self._uncached_fn()
        self.assertEqual(self._call_counts['_uncached_fn'], 2, 'The cached value was used when the function should have been called again.')
