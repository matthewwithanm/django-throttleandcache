import os
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys


read = lambda fname: open(os.path.join(os.path.dirname(__file__), fname)).read()


README = read('README.rst')


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['tests', '-s']
        self.test_suite = True

    def run_tests(self):
        import pytest
        os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
        errno = pytest.main(self.test_args)
        sys.exit(errno)


# Load package meta from the pkgmeta module without loading throttleandcache.
pkgmeta = {}
execfile(os.path.join(os.path.dirname(__file__),
         'throttleandcache', 'pkgmeta.py'), pkgmeta)


setup(
    name='django-throttleandcache',
    version=pkgmeta['__version__'],
    description='A utility for caching/throttling function calls.',
    url='http://github.com/matthewwithanm/django-throttleandcache',
    license='BSD',
    long_description=README,
    author=pkgmeta['__author__'],
    author_email='m@tthewwithanm.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'python-dateutil<2.0a',
        'django-appconf>=0.5',
    ],
    tests_require=[
        'pytest==2.3.5',
        'mock==1.0.1',
        'Django',
        'celery',
    ],
    extras_require={
        'async': ['celery>=3.0'],
    },
    cmdclass={'test': PyTest},
    zip_safe=False,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
