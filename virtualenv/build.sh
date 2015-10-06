#!/bin/bash

set -e
set -x

if [ -z "$1" ]; then
    echo "Usage: ./build.sh [all|env_name]"
    exit
fi

cd $(dirname "${BASH_SOURCE[0]}")

if [ "$1" = "all" ] || [ "$1" = "py2neo208" ]; then
    rm -rf py2neo208
    virtualenv --python=python2.7 py2neo208
    source py2neo208/bin/activate
    pip install ipython
    pip install "py2neo==2.0.8"
    pip install simplejson
    pip install pytest
    ln -s ../../../../../neolixir py2neo208/lib/python*/site-packages/
fi
