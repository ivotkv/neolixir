#!/bin/bash

set -e
set -x

if [ -z "$1" ]; then
    echo "Usage: ./build.sh [all|env_name]"
    exit
fi

cd $(dirname "${BASH_SOURCE[0]}")

if [ "$1" = "all" ] || [ "$1" = "py2neo14" ]; then
    rm -rf py2neo14
    virtualenv py2neo14
    source py2neo14/bin/activate
    pip install "py2neo==1.4.6"
    pip install pytest
    ln -s ../../../../../neolixir py2neo14/lib/python*/site-packages/
fi

if [ "$1" = "all" ] || [ "$1" = "py2neo16" ]; then
    rm -rf py2neo16
    virtualenv py2neo16
    source py2neo16/bin/activate
    pip install "py2neo>=1.6,<1.7"
    pip install pytest
    ln -s ../../../../../neolixir py2neo16/lib/python*/site-packages/
fi

if [ "$1" = "all" ] || [ "$1" = "py2neo2beta" ]; then
    rm -rf py2neo2beta
    virtualenv py2neo2beta
    source py2neo2beta/bin/activate
    pip install "git+git://github.com/nigelsmall/py2neo.git@beta/2.0#egg=py2neo"
    pip install pytest
    ln -s ../../../../../neolixir py2neo2beta/lib/python*/site-packages/
fi
