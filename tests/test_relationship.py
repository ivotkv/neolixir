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
    r = TRel((n1, 'test', n2))
    m.session.commit()
    assert r.id is not None
    r_id = r.id

    m.session.clear()
    r = Relationship(r_id)
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
        Relationship(r_id)
