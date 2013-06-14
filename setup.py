from distutils.core import setup
import os
from setuptools.command.test import test as TestCommand
import sys


read = lambda fname: open(os.path.join(os.path.dirname(__file__), fname)).read()


README = read('README.markdown')


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


setup(
    name='django-throttleandcache',
    version="0.1",
    description='A utility for caching/throttling function calls.',
    url='http://github.com/matthewwithanm/django-throttleandcache',
    license='BSD',
    long_description=README,

    author='Matthew Tretter',
    author_email='m@tthewwithanm.com',
    packages=[
        'throttleandcache',
    ],
    package_data={'throttleandcache': []},
    requires=[],
    tests_require=[
        'pytest==2.3.5',
        'mock==1.0.1',
        'Django',
    ],
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
