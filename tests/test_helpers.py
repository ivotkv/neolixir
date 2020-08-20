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

def test_create_out_of_session(m):
    n = TNode()
    randval = n.randval = n.randval
    assert m.session.count == 1

    ret = create_out_of_session(m, n)
    assert m.session.count == 0
    assert isinstance(ret, int)

    n = TNode.get(ret)
    assert m.session.count == 1
    assert n.randval == randval

def test_update_out_of_session(m):
    n = TNode()
    n.string = 'value1'
    m.session.commit()
    assert n in m.session
    n.properties.reload()
    assert n.string == 'value1'

    ret = update_out_of_session(m, n, {'string': 'value2'})
    assert ret == True
    assert n in m.session
    assert n.string == 'value1'

    n.properties.reload()
    assert n.string == 'value2'

def test_delete_out_of_session(m):
    n = TNode()
    m.session.commit()
    assert not n.is_phantom()
    n_id = n.id

    ret = delete_out_of_session(m, n)
    assert ret == True
    assert m.session.count == 1
    assert n in m.session
    assert not n.is_deleted()

    m.session.clear()
    with raises(EntityNotFoundException):
        TNode.get(n_id)

    m.session.clear()

    n1 = TNode()
    n2 = TNode()
    rel = n1.rel_out.append(n2)
    m.session.commit()
    assert not rel.is_phantom()
    rel_id = rel.id

    ret = delete_out_of_session(m, rel)
    assert ret == True
    assert m.session.count == 3
    assert rel in m.session
    assert not rel.is_deleted()

    m.session.clear()
    with raises(EntityNotFoundException):
        Relationship.get(rel_id)

def test_append_out_of_session(m):
    n1 = TNode()
    n2 = TNode()
    m.session.commit()
    assert n2 not in n1.rel_out

    ret = append_out_of_session(m, n1, 'rel_out', n2)
    assert isinstance(ret, int)
    assert m.session.count == 2
    assert n2 not in n1.rel_out

    n1.rel_out.load()
    assert n2 in n1.rel_out
    assert n1.rel_out.rel(n2).id == ret

def test_remove_out_of_session(m):
    n1 = TNode()
    n2 = TNode()
    rel = n1.rel_out.append(n2)
    m.session.commit()
    assert n2 in n1.rel_out

    n1_id = n1.id
    n2_id = n2.id
    rel_id = rel.id

    ret = remove_out_of_session(m, n1, 'rel_out', n2)
    assert ret == True
    assert m.session.count == 3
    assert n2 in n1.rel_out

    m.session.clear()
    n1 = TNode.get(n1_id)
    n2 = TNode.get(n2_id)
    assert n2 not in n1.rel_out
    with raises(EntityNotFoundException):
        Relationship.get(rel_id)
