#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

VERSION = '0.63'

setup(
    name='neolixir',
    description='Declarative ORM abstraction layer for Neo4j',
    version=VERSION,
    packages=['neolixir'],
    install_requires=[
        'py2neo==1.4.6'
    ],
    test_requires=[
        'pytest'
    ]
)
