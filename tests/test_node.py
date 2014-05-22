from common import *

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
    with raises(ResourceNotFound):
        Node(n1_id)
