from common import *

def test_index(m):
    batch = m.batch()
    index = NodeIndex('BatchTestIndex')
    index.clear()

    # test creating and uniqueness
    batch.index(index, 'node', '1', TNode())
    batch.submit()
    n1 = index.get('node', '1')[0]
    assert len(m.session.phantomnodes) == 0
    assert len(m.session.nodes) == 1
    assert isinstance(n1, TNode)

    batch.index(index, 'node', '1', TNode())
    batch.submit()
    assert len(index.get('node', '1')) == 1
    assert index.get('node', '1')[0] is n1
    assert len(m.session.phantomnodes) == 0
    assert len(m.session.nodes) == 1

    # test indexing an existing node
    batch.index(index, 'node', '2', n1)
    batch.submit()
    assert n1 in m.session.nodes.values()
    assert len(index.get('node', '2')) == 1
    assert index.get('node', '2')[0] is n1

    batch.index(index, 'node', '2', n1)
    batch.index(index, 'node', '2', TNode())
    batch.submit()
    assert len(m.session.phantomnodes) == 0
    assert len(m.session.nodes) == 1
    assert n1 in m.session.nodes.values()
    assert len(index.get('node', '2')) == 1
    assert index.get('node', '2')[0] is n1

    # test return values
    def callback(n1, response):
        assert response is n1
    batch.index(index, 'node', '3', n1)
    batch.request_callback(callback, n1)
    batch.index(index, 'node', '3', TNode())
    batch.request_callback(callback, n1)
    batch.submit()

    def callback(m, cls, response):
        assert isinstance(response, cls)
        assert index.get('node', '4')[0] is response
        assert len(m.session.phantomnodes) == 0
    batch.index(index, 'node', '4', TNode())
    batch.request_callback(callback, m, TNode)
    batch.submit()

    n2 = TNode()
    def callback(m, n2, response):
        assert response is n2
        assert len(m.session.phantomnodes) == 0
    batch.index(index, 'node', '5', n2)
    batch.request_callback(callback, m, n2)
    batch.submit()

    # test that __instance_of__ relationship was created
    assert n1 in TNode.query.all()

    # test indexed creates with relationships
    n1 = TNode()
    n2 = TNode()
    rel = n1.rel_out.append(n2)
    batch.create(n1)
    #batch.index(index, 'node', '6', n1) # TODO: is there a workaround to make this work?
    batch.index(index, 'node', '7', n2)
    batch.create(rel)
    def callback(rel, response):
        assert response is rel._entity
        assert response.start_node == n1._entity
        assert response.end_node == n2._entity
    batch.request_callback(callback, rel)
    batch.submit()

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
