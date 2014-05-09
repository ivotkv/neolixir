#!/bin/bash

set -e
set -x

cd $(dirname "${BASH_SOURCE[0]}")

rm -rf py2neo14
virtualenv py2neo14
source py2neo14/bin/activate
pip install "py2neo==1.4.6"
pip install pytest
ln -s ../../../../../neolixir py2neo14/lib/python*/site-packages/

rm -rf py2neo16
virtualenv py2neo16
source py2neo16/bin/activate
pip install "py2neo>=1.6,<1.7"
pip install pytest
ln -s ../../../../../neolixir py2neo16/lib/python*/site-packages/
