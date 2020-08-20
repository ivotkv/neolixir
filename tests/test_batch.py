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
from py2neo import neo4j

def test_index(m):
    batch = m.batch()
    index = NodeIndex('BatchTestIndex')
    index.clear()

    # test creating and uniqueness
    n1 = TNode()
    assert n1.is_phantom()
    assert len(m.session.phantomnodes) == 1
    assert len(m.session.nodes) == 0
    batch.index(index, 'node', '1', n1)
    batch.submit()
    assert len(batch.jobs) == 0
    assert not n1.is_phantom()
    assert len(m.session.phantomnodes) == 0
    assert len(m.session.nodes) == 1
    assert index.get('node', '1')[0] is n1

    batch.index(index, 'node', '1', TNode())
    batch.submit()
    assert len(batch.jobs) == 0
    assert len(index.get('node', '1')) == 1
    assert index.get('node', '1')[0] is n1
    assert len(m.session.phantomnodes) == 0
    assert len(m.session.nodes) == 1

    # test indexing an existing node
    batch.index(index, 'node', '2', n1)
    batch.submit()
    assert len(batch.jobs) == 0
    assert n1 in m.session.nodes.values()
    assert len(index.get('node', '2')) == 1
    assert index.get('node', '2')[0] is n1

    batch.index(index, 'node', '2', n1)
    batch.index(index, 'node', '2', TNode())
    batch.submit()
    assert len(batch.jobs) == 0
    assert len(m.session.phantomnodes) == 0
    assert len(m.session.nodes) == 1
    assert n1 in m.session.nodes.values()
    assert len(index.get('node', '2')) == 1
    assert index.get('node', '2')[0] is n1

    # test return values
    def callback(n1, response):
        assert response is n1
    batch.index(index, 'node', '3', n1)
    batch.job_callback(callback, n1)
    batch.index(index, 'node', '3', TNode())
    batch.job_callback(callback, n1)
    batch.submit()
    assert len(batch.jobs) == 0

    def callback(m, cls, response):
        assert isinstance(response, cls)
        assert index.get('node', '4')[0] is response
        assert len(m.session.phantomnodes) == 0
    batch.index(index, 'node', '4', TNode())
    batch.job_callback(callback, m, TNode)
    batch.submit()
    assert len(batch.jobs) == 0

    n2 = TNode()
    def callback(m, n2, response):
        assert response is n2
        assert len(m.session.phantomnodes) == 0
    batch.index(index, 'node', '5', n2)
    batch.job_callback(callback, m, n2)
    batch.submit()
    assert len(batch.jobs) == 0

    # test that node was labeled correctly
    assert n1 in TNode.query.all()

    # test indexed creates with relationships
    n1 = TNode()
    n2 = TNode()
    rel = n1.rel_out.append(n2)
    batch.create(n1)
    #batch.index(index, 'node', '6', n1) # TODO: is there a workaround to make this work?
    batch.index(index, 'node', '7', n2)
    batch.submit() # NOTE: separate submit until same-batch creates are supported
    batch.create(rel)
    def callback(batch, rel, response):
        # need to resubmit if needed to fake during-commit behaviour
        if batch.resubmit:
            batch.submit()
        assert response is rel._entity
        assert response.start_node == n1._entity
        assert response.end_node == n2._entity
    batch.job_callback(callback, batch, rel)
    batch.submit()
    assert len(batch.jobs) == 0

def test_index_committing(m):
    m.session.committing = True
    test_index(m)
    m.session.committing = False    

def test_cypher(m):
    batch = m.batch()

    n1 = TNode()
    m.session.commit()
    assert isinstance(n1.id, int)

    batch.cypher("start n=node({n_id}) return n", params={'n_id': n1.id}, automap=False)
    result = batch.submit()[0]
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], list)
    assert len(result[0]) == 1
    assert isinstance(result[0][0], neo4j.Node)
    assert result[0][0] == n1._entity

    assert len(batch.jobs) == 0

    batch.cypher("start n=node({n_id}) return n", params={'n_id': n1.id}, automap=True)
    result = batch.submit()[0]
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], list)
    assert len(result[0]) == 1
    assert result[0][0] is n1

def test_commit_batch_size(m):
    nodes = [TNode() for x in range(20)]
    for idx, node in enumerate(nodes):
        try:
            node.rel_out.append(nodes[idx + 1])
        except IndexError:
            pass

    m.session.commit(batched=True, batch_size=5)

    for idx, node in enumerate(nodes):
        assert not node.is_phantom()
        try:
            assert not node.rel_out.rel(nodes[idx + 1]).is_phantom()
        except IndexError:
            pass
