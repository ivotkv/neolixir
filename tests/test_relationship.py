from common import *

def test_expunge(m):
    n1 = TNode()
    n2 = TNode()
    rel = n1.rel_out.append(n2)
    assert n1 in m.session.phantomnodes
    assert n2 in m.session.phantomnodes
    assert rel in m.session.relmap
    n1.expunge()
    assert n1 not in m.session.phantomnodes
    assert n2 in m.session.phantomnodes
    assert rel not in m.session.relmap

def test_save_load_delete(m):
    n1 = TNode()
    n2 = TNode()
    r = TRel.get((n1, 'test', n2))
    m.session.commit()
    assert r.id is not None
    r_id = r.id

    m.session.clear()
    r = Relationship.get(r_id)
    assert r.id == r_id
    assert isinstance(r, TRel)
    assert r.type == 'test'
    assert isinstance(r.start, TNode)
    assert isinstance(r.end, TNode)

    n1 = r.start
    n2 = r.end
    n1.delete()
    assert r.is_deleted()
    assert not n2.is_deleted()
    m.session.commit()
    with raises(EntityNotFoundException):
        Relationship.get(r_id)

def test_load_with_deleted_end_node(m):
    n1 = TNode()
    n2 = TNode()
    rel = n1.trel_out.append(n2)
    m.session.commit()
    n1_id = n1.id
    n2_id = n2.id
    rel_id = rel.id
    m.session.clear()

    # through relview
    n1 = TNode.get(n1_id)
    n2 = TNode.get(n2_id)
    n2.delete()
    assert m.session.count == 2
    assert n2 not in n1.trel_out
    assert m.session.count == 3
    rel = TRel.get(rel_id)
    assert rel in m.session
    assert rel.is_deleted()
    assert m.session.count == 3
    m.session.clear()

    # direct load
    n1 = TNode.get(n1_id)
    n1.delete()
    assert m.session.count == 1
    rel = TRel.get(rel_id)
    assert rel in m.session
    assert rel.is_deleted()
    n2 = TNode.get(n2_id)
    assert rel not in n2.trel_in
    assert m.session.count == 3
