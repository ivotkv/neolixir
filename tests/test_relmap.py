from common import *

def test_contains_iter_len(m):
    n1 = TNode()
    n2 = TNode()
    r1 = Relationship.get((n1, 'test1', n2))
    assert r1 in m.session.relmap
    assert r1 in iter(m.session.relmap)
    assert len(list(iter(m.session.relmap))) == 1
    assert len(m.session.relmap) == 1

    m.session.commit()
    assert r1 in m.session.relmap
    assert r1 in iter(m.session.relmap)
    assert len(list(iter(m.session.relmap))) == 1
    assert len(m.session.relmap) == 1

    r2 = Relationship.get((n1, 'test2', n2))
    assert r2 in m.session.relmap
    assert r2 in iter(m.session.relmap)
    assert len(list(iter(m.session.relmap))) == 2
    assert len(m.session.relmap) == 2

    r1.expunge()
    assert r1 not in m.session.relmap
    assert r1 not in iter(m.session.relmap)
    assert len(list(iter(m.session.relmap))) == 1
    assert len(m.session.relmap) == 1

    r2.expunge()
    assert r1 not in m.session.relmap
    assert r1 not in iter(m.session.relmap)
    assert len(list(iter(m.session.relmap))) == 0
    assert len(m.session.relmap) == 0

def test_mapper(m):
    relmap = m.session.relmap
    n1 = TNode()
    n2 = TNode()
    r = Relationship.get((n1, 'test', n2))
    assert r.start is n1
    assert r.type is 'test'
    assert r.end is n2
    assert r in relmap.start[(n1, 'test')]
    assert r in relmap.end[(n2, 'test')]
    r.delete()
    assert r not in relmap.start[(n1, 'test')]
    assert r not in relmap.end[(n2, 'test')]

def test_index_map(m):
    n1 = TNode()
    n2 = TNode()
    n1.trel_out.append(n2)
    assert n1.trel_out[0] is n2
    assert isinstance(n1.trel_out.rel(n1.trel_out[0]), TRel)
    assert n1.trel_out.node(n1.trel_out.rel(n1.trel_out[0])) is n2
