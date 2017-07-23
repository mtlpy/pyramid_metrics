import os
from setuptools import setup, find_packages

install_requires = [
    'statsd >= 2.1.2, < 2.2',
]


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='pyramid_metrics',
    version='0.3.1.dev0',
    author='Pior Bastida',
    author_email='pior@pbastida.net',
    description='Performance metrics for Pyramid using StatsD',
    license='BSD',
    keywords='wsgi pylons pyramid statsd metric tween handler',
    url='https://github.com/ludia/pyramid_metrics',
    long_description=read('README.rst'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: Pyramid',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
    ],
    packages=find_packages(),
    package_data={
        'devup': ['files/*'],
    },
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'de = devup.app:cli',
        ],
    },
)
