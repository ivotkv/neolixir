#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from neolixir import __name__, __package__, __version__

setup(
    name=__name__,
    description='Declarative ORM abstraction layer for Neo4j',
    version=__version__,
    packages=[__package__],
    install_requires=[
        'py2neo>=2.0',
        'simplejson'
    ],
    test_requires=[
        'pytest'
    ]
)
