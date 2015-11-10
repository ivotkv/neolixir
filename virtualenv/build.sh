#!/bin/bash

set -e
set -x

cd $(dirname "${BASH_SOURCE[0]}")

VERSIONS=${VERSIONS:-"2.0.8"}

for VERSION in $VERSIONS; do
    DIRNAME="py2neo-$VERSION"
    rm -rf $DIRNAME
    virtualenv --python=python2.7 $DIRNAME
    source $DIRNAME/bin/activate
    pip install --upgrade pip
    pip install ipython
    pip install "py2neo==$VERSION"
    pip install simplejson
    pip install pytest
    ln -s ../../../../../neolixir $DIRNAME/lib/python*/site-packages/
done
