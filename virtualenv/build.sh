#!/bin/bash

set -e
set -x

cd $(dirname "${BASH_SOURCE[0]}")

PYTHON_VERSION=${PYTHON_VERSION:-"2.7"}
PY2NEO_VERSION=${PY2NEO_VERSION:-"2.0.8"}

DIRNAME="python-$PYTHON_VERSION-py2neo-$PY2NEO_VERSION"

# build clean virtualenv
rm -rf $DIRNAME
virtualenv --python=python$PYTHON_VERSION $DIRNAME
source $DIRNAME/bin/activate

# install standard packages
pip install --upgrade pip
pip install ipython
pip install pytest

# install neolixir dependencies
pip install "py2neo==$PY2NEO_VERSION"
pip install simplejson

# symlink neolixir into virtualenv for convenience
ln -s ../../../../../neolixir $DIRNAME/lib/python$PYTHON_VERSION/site-packages/
