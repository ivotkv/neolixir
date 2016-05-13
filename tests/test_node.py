# -*- coding: utf-8 -*-
# 
# The MIT License (MIT)
# 
# Copyright (c) 2013 Ivaylo Tzvetkov, ChallengeU
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 

from common import *

def test_create(m):
    assert m.session.count == 0

    # test save id
    n1 = TNode()
    assert m.session.count == 1
    assert n1.id is None
    assert n1 in m.session.phantomnodes
    assert len(m.session.nodes) == 0
    assert m.session.new == 1
    assert m.session.dirty == 0
    assert m.session.is_dirty()

    n1.string = "test_commit"
    assert m.session.new == 1
    assert m.session.dirty == 0
    assert m.session.is_dirty()

    m.session.commit()
    assert m.session.count == 1
    assert isinstance(n1.id, int)
    assert n1 not in m.session.phantomnodes
    assert n1.id in m.session.nodes
    assert m.session.nodes[n1.id] is n1
    assert Node.get(n1.id) is n1

    # test load by id
    n1_id = n1.id
    m.session.clear()
    n1 = Node.get(n1_id)
    assert isinstance(n1, TNode)
    assert n1.id == n1_id
    assert n1.string == "test_commit"
    assert Node.get(n1_id) is n1

    # test load after expunge
    n1.expunge()
    assert Node.get(n1_id) is not n1
    assert Node.get(n1_id) is Node.get(n1_id)

def test_delete(m):
    # phantom nodes
    n1 = TNode()
    assert not n1.is_deleted()
    assert m.session.count == 1
    n1.delete()
    assert n1.is_deleted()
    assert m.session.count == 0

    # existing nodes
    n1 = TNode()
    m.session.commit()
    n1_id = n1.id
    assert m.session.dirty == 0
    n1.delete()
    assert n1.is_deleted()
    assert m.session.dirty == 1
    m.session.commit()
    assert m.session.count == 0
    with raises(EntityNotFoundException):
        Node.get(n1_id)

    # with relationships
    n1 = TNode()
    n2 = TNode()
    rel = n1.trel_out.append(n2)
    m.session.commit()
    assert rel in n1.trel_out
    assert rel in n2.trel_in
    n1.delete()
    assert n1 in m.session
    assert n1.is_deleted()
    assert not n2.is_deleted()
    assert rel.is_deleted()
    assert rel in m.session
    assert rel not in n1.trel_out
    assert rel not in n2.trel_in
