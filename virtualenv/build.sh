#!/bin/bash

set -e
set -x

if [ -z "$1" ]; then
    echo "Usage: ./build.sh [all|env_name]"
    exit
fi

cd $(dirname "${BASH_SOURCE[0]}")

if [ "$1" = "all" ] || [ "$1" = "py2neo204" ]; then
    rm -rf py2neo204
    virtualenv --python=python2.7 py2neo204
    source py2neo204/bin/activate
    pip install ipython
    pip install "py2neo==2.0.4"
    pip install simplejson
    pip install pytest
    ln -s ../../../../../neolixir py2neo204/lib/python*/site-packages/
fi
