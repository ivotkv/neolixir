from common import *

def test_clear(m):
    assert m.session.count == 0
    n1 = TNode()
    assert m.session.count == 1
    n2 = TNode()
    assert m.session.count == 2
    m.session.clear()
    assert m.session.count == 0

def test_expunge(m):
    assert m.session.count == 0
    n1 = TNode()
    assert m.session.count == 1
    n1.expunge()
    assert m.session.count == 0

def test_commit(m):
    # test save id
    n1 = TNode()
    n1.string = "test_commit"
    assert n1.id is None
    m.session.commit()
    assert isinstance(n1.id, int)
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
