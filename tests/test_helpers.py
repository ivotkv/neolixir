from common import *

def test_create_out_of_session(m):
    n = TNode()
    randval = n.randval = n.randval
    assert m.session.count == 1

    ret = create_out_of_session(m, n)
    assert m.session.count == 0
    assert isinstance(ret, int)

    n = TNode(ret)
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
        TNode(n_id)

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
    n1 = TNode(n1_id)
    n2 = TNode(n2_id)
    assert n2 not in n1.rel_out
    with raises(EntityNotFoundException):
        Relationship(rel_id)
