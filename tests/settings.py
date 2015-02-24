SECRET_KEY = '2@4p=l!t7c1d@pmo%aavvm_ngzyi8=$!lmfhkk@alxc=0q(##u'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'test-cache',
    }
}
