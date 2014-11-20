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
    assert Node(n1.id) is n1

    # test load by id
    n1_id = n1.id
    m.session.clear()
    n1 = Node(n1_id)
    assert isinstance(n1, TNode)
    assert n1.id == n1_id
    assert n1.string == "test_commit"
    assert Node(n1_id) is n1

    # test load after expunge
    n1.expunge()
    assert Node(n1_id) is not n1
    assert Node(n1_id) is Node(n1_id)

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
        Node(n1_id)
