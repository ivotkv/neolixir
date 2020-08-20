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

from common import *

def test_init(m):
    n1 = InitNode()
    assert n1.counter == 1
    m.session.commit()
    assert n1.counter == 1
    assert InitNode.get(n1.id) is n1
    assert InitNode.get(n1.id).counter == 1
    m.session.clear()
    assert InitNode.get(n1.id) is not n1
    assert InitNode.get(n1.id).counter == 2

def test_interface_inheritance(m):
    assert hasattr(IFieldTNode, 'ifield')
    assert 'ifield' in IFieldTNode._descriptors
    assert IFieldTNode.ifield.name == 'ifield'

    n1 = IFieldTNode()
    assert hasattr(n1, 'ifield')
    assert 'ifield' in n1._descriptors
    assert n1.ifield is None

    n1.ifield = 'ifield'
    assert n1.ifield == 'ifield'
    assert n1.properties['ifield'] == 'ifield'

    m.session.commit()
    n1_id = n1.id
    m.session.clear()
    n1 = Node.get(n1_id)
    assert isinstance(n1, IFieldTNode)
    assert hasattr(n1, 'ifield')
    assert 'ifield' in n1._descriptors
    assert n1.ifield == 'ifield'
    assert n1.properties['ifield'] == 'ifield'
