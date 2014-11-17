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
    pip install ipython
    pip install "py2neo==1.4.6"
    pip install pytest
    ln -s ../../../../../neolixir py2neo14/lib/python*/site-packages/
fi

if [ "$1" = "all" ] || [ "$1" = "py2neo20" ]; then
    rm -rf py2neo20
    virtualenv-2.7 py2neo20
    source py2neo20/bin/activate
    pip install ipython
    pip install "py2neo==2.0"
    pip install pytest
    ln -s ../../../../../neolixir py2neo20/lib/python*/site-packages/
fi
