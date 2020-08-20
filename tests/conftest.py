# -*- coding: utf-8 -*-
# 
# The MIT License (MIT)
# 
# Copyright (c) 2013 Ivo Tzvetkov
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 

import os
import pytest
import warnings

warnings.simplefilter("error")

@pytest.fixture(scope='session')
def metadata():
    from py2neo.error import GraphError
    from neolixir import metadata
    if 'NEO4J_TEST_SERVER' in os.environ:
        metadata.url = 'http://{0}/db/data/'.format(os.environ['NEO4J_TEST_SERVER'])
    try:
        from py2neo import Unauthorized
        try:
            metadata.version
        except Unauthorized:
            metadata.authenticate('neo4j', 'neo4j')
    except ImportError:
        pass
    try:
        metadata.graph.delete_all()
    except GraphError as e:
        if str(e).find('response 403') > 0:
            metadata.change_password('neo4j', 'neo4j', 'testpass')
            metadata.change_password('neo4j', 'testpass', 'neo4j')
            metadata.graph.delete_all()
        else:
            raise e
    import models
    metadata.init()
    return metadata

@pytest.fixture()
def m(metadata):
    metadata.session.clear()
    return metadata
