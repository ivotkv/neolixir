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
from decimal import Decimal
from datetime import datetime

def test_node_properties(m):
    n1 = TNode()
    assert n1.is_dirty() == False
    n1.properties['prop1'] = 'prop1'
    assert n1.properties['prop1'] == 'prop1'
    assert n1.is_dirty() == True
    m.session.commit()
    assert n1.is_dirty() == False

    n1.properties['prop1'] = 'prop1'
    assert n1.properties['prop1'] == 'prop1'
    assert n1.is_dirty() == False
    n1.properties['prop1'] = 'prop1-changed'
    assert n1.properties['prop1'] == 'prop1-changed'
    assert n1.is_dirty() == True
    m.session.commit()

    n1_id = n1.id
    n1_entity = n1._entity
    m.session.clear()
    n1 = Node.get(n1_id)
    assert n1._entity is not n1_entity
    assert n1.is_dirty() == False
    assert n1.properties['prop1'] == 'prop1-changed'

def test_rel_properties(m):
    n1 = TNode()
    n2 = TNode()
    rel = n1.rel_out.append(n2)
    assert rel.is_dirty() == False
    rel.properties['prop1'] = 'prop1'
    assert rel.properties['prop1'] == 'prop1'
    assert rel.is_dirty() == True
    m.session.commit()
    assert rel.is_dirty() == False

    rel.properties['prop1'] = 'prop1'
    assert rel.properties['prop1'] == 'prop1'
    assert rel.is_dirty() == False
    rel.properties['prop1'] = 'prop1-changed'
    assert rel.properties['prop1'] == 'prop1-changed'
    assert rel.is_dirty() == True
    m.session.commit()

    rel_id = rel.id
    rel_entity = rel._entity
    m.session.clear()
    rel = Relationship.get(rel_id)
    assert rel._entity is not rel_entity
    assert rel.is_dirty() == False
    assert rel.properties['prop1'] == 'prop1-changed'

def test_null(m):
    n1 = TNode()
    n1.properties['prop1'] = 'prop1'
    n1.properties['prop2'] = None
    m.session.commit()

    n1_id = n1.id
    m.session.clear()
    n1 = Node.get(n1_id)
    assert n1.properties['prop1'] == 'prop1'
    assert 'prop2' not in n1.properties

    n1.properties['prop1'] = None
    m.session.commit()
    m.session.clear()
    n1 = Node.get(n1_id)
    assert 'prop1' not in n1.properties

def test_string(m):
    n1 = TNode()
    assert n1.is_dirty() == False
    assert n1.string == None
    assert n1.default_string == 'default'

def test_enum(m):
    n1 = TNode()
    assert n1.is_dirty() == False
    assert n1.enum == None
    assert n1.default_enum == 'value1'

    n1.enum = 'value1'
    assert n1.enum == 'value1'
    with raises(ValueError):
        n1.enum = 'invalid'
    assert n1.enum == 'value1'
    n1.enum = None
    assert n1.enum == None

def test_numeric(m):
    n1 = TNode()
    n1.numeric = 1
    assert n1.properties['numeric'] == '1'
    n1.numeric = 1.5
    assert n1.properties['numeric'] == '1.5'
    n1.numeric = '1.6'
    assert n1.properties['numeric'] == '1.6'
    n1.numeric = Decimal('1.7')
    assert n1.properties['numeric'] == '1.7'
    with raises(ValueError):
        n1.numeric = 'invalid'
    with raises(ValueError):
        n1.numeric = False
    with raises(ValueError):
        n1.numeric = object()
    assert n1.properties['numeric'] == '1.7'
    n1.numeric = None
    assert n1.properties['numeric'] == None

def test_datetime(m):
    n1 = TNode()
    dt = datetime.now()
    n1.datetime = dt
    assert n1.properties['datetime'] == dt.strftime("%Y-%m-%d %H:%M:%S")
    n1.datetime = '2015-10-10 10:10:10'
    assert n1.properties['datetime'] == '2015-10-10 10:10:10'
    n1.datetime = '2015-10-10 10:10'
    assert n1.properties['datetime'] == '2015-10-10 10:10:00'
    n1.datetime = '2015-10-10'
    assert n1.properties['datetime'] == '2015-10-10 00:00:00'
    n1.datetime = '2015-10-10T10:10:10'
    assert n1.properties['datetime'] == '2015-10-10 10:10:10'
    n1.datetime = '2015-10-10 10:10:10.123'
    assert n1.properties['datetime'] == '2015-10-10 10:10:10'
    with raises(ValueError):
        n1.datetime = 'invalid'
    with raises(ValueError):
        n1.datetime = False
    with raises(ValueError):
        n1.datetime = object()
    assert n1.properties['datetime'] == '2015-10-10 10:10:10'
    n1.datetime = None
    assert n1.properties['datetime'] == None
