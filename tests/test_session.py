from Queue import Queue
from threading import Thread
from common import *

def test_counts_and_clear(m):
    assert m.session.count == 0
    assert m.session.new == 0
    assert m.session.dirty == 0
    assert not m.session.is_dirty()
    assert len(m.session.nodes) == 0
    assert len(m.session.phantomnodes) == 0
    assert len(m.session.relmap) == 0
    assert len(m.session.propmap) == 0

    n1 = TNode()
    assert m.session.count == 1
    assert m.session.new == 1
    assert m.session.dirty == 0
    assert m.session.is_dirty()
    assert len(m.session.nodes) == 0
    assert len(m.session.phantomnodes) == 1
    assert len(m.session.relmap) == 0
    assert len(m.session.propmap) == 0

    m.session.commit()
    assert m.session.count == 1
    assert m.session.new == 0
    assert m.session.dirty == 0
    assert not m.session.is_dirty()
    assert len(m.session.nodes) == 1
    assert len(m.session.phantomnodes) == 0
    assert len(m.session.relmap) == 0
    assert len(m.session.propmap) == 1

    n1.string = "test"
    assert m.session.count == 1
    assert m.session.new == 0
    assert m.session.dirty == 1
    assert m.session.is_dirty()
    assert len(m.session.nodes) == 1
    assert len(m.session.phantomnodes) == 0
    assert len(m.session.relmap) == 0
    assert len(m.session.propmap) == 1
    
    n2 = TNode()
    assert m.session.count == 2
    assert m.session.new == 1
    assert m.session.dirty == 1
    assert m.session.is_dirty()
    assert len(m.session.nodes) == 1
    assert len(m.session.phantomnodes) == 1
    assert len(m.session.relmap) == 0
    assert len(m.session.propmap) == 1

    r = n1.trel_out.append(n2)
    assert m.session.count == 3
    assert m.session.new == 2
    assert m.session.dirty == 1
    assert m.session.is_dirty()
    assert len(m.session.nodes) == 1
    assert len(m.session.phantomnodes) == 1
    assert len(m.session.relmap) == 1
    assert len(m.session.propmap) == 1

    m.session.clear()
    assert m.session.count == 0
    assert m.session.new == 0
    assert m.session.dirty == 0
    assert not m.session.is_dirty()
    assert len(m.session.nodes) == 0
    assert len(m.session.phantomnodes) == 0
    assert len(m.session.relmap) == 0
    assert len(m.session.propmap) == 0

def test_new_and_dirty(m):
    assert m.session.new == 0
    assert m.session.dirty == 0
    assert not m.session.is_dirty()

    n1 = TNode()
    assert m.session.new == 1
    assert m.session.dirty == 0
    assert m.session.is_dirty()

    n2 = TNode()
    r1 = n1.trel_out.append(n2)
    assert m.session.new == 3
    assert m.session.dirty == 0
    assert m.session.is_dirty()

    m.session.commit()
    assert m.session.new == 0
    assert m.session.dirty == 0
    assert not m.session.is_dirty()

    n3 = TNode()
    assert m.session.new == 1
    assert m.session.dirty == 0
    assert m.session.is_dirty()

    n3.string = 'test'
    assert m.session.new == 1
    assert m.session.dirty == 0
    assert m.session.is_dirty()
    
    m.session.commit()
    assert m.session.new == 0
    assert m.session.dirty == 0
    assert not m.session.is_dirty()

    r2 = n1.trel_out.append(n3)
    assert m.session.new == 1
    assert m.session.dirty == 0
    assert m.session.is_dirty()
    
    m.session.commit()
    assert m.session.new == 0
    assert m.session.dirty == 0
    assert not m.session.is_dirty()

    n1.string = 'test'
    assert n1.is_dirty()
    assert m.session.new == 0
    assert m.session.dirty == 1
    assert m.session.is_dirty()
    assert n1.string == 'test'
    
    m.session.commit()
    assert m.session.new == 0
    assert m.session.dirty == 0
    assert not m.session.is_dirty()
    assert n1.string == 'test'

    n1.string = 'test'
    assert not n1.is_dirty()
    assert m.session.new == 0
    assert m.session.dirty == 0
    assert not m.session.is_dirty()
    assert n1.string == 'test'

    r1.string = 'test'
    assert r1.is_dirty()
    assert m.session.new == 0
    assert m.session.dirty == 1
    assert m.session.is_dirty()
    assert r1.string == 'test'
    
    m.session.commit()
    assert m.session.new == 0
    assert m.session.dirty == 0
    assert not m.session.is_dirty()
    assert r1.string == 'test'

    r1.string = 'test'
    assert not r1.is_dirty()
    assert m.session.new == 0
    assert m.session.dirty == 0
    assert not m.session.is_dirty()
    assert r1.string == 'test'

def test_add(m):
    n1 = TNode()
    n2 = TNode()
    r = n1.trel_out.append(n2)
    assert m.session.count == 3
    assert m.session.new == 3
    assert m.session.dirty == 0
    assert m.session.is_dirty()
    assert len(m.session.nodes) == 0
    assert len(m.session.phantomnodes) == 2
    assert len(m.session.relmap) == 1
    assert len(m.session.propmap) == 0

    m.session.add(n1)
    m.session.add(n2)
    m.session.add(r)
    assert m.session.count == 3
    assert m.session.new == 3
    assert m.session.dirty == 0
    assert m.session.is_dirty()
    assert len(m.session.nodes) == 0
    assert len(m.session.phantomnodes) == 2
    assert len(m.session.relmap) == 1
    assert len(m.session.propmap) == 0

    m.session.clear()
    m.session.add(n1)
    assert n1 in m.session.phantomnodes
    m.session.add(n2)
    assert n2 in m.session.phantomnodes
    m.session.add(r)
    assert r in m.session.relmap

    assert m.session.count == 3
    assert m.session.new == 3
    assert m.session.dirty == 0
    assert m.session.is_dirty()
    assert len(m.session.nodes) == 0
    assert len(m.session.phantomnodes) == 2
    assert len(m.session.relmap) == 1
    assert len(m.session.propmap) == 0

def test_get(m):
    n1 = TNode()
    n2 = TNode()
    r = n1.trel_out.append(n2)
    m.session.commit()

    assert m.session.get(n1._entity) is n1
    assert m.session.get(m.graph.node(n1.id)) is n1
    assert m.session.get(n2._entity) is n2
    assert m.session.get(m.graph.node(n2.id)) is n2
    assert m.session.get(r._entity) is r
    assert m.session.get(m.graph.relationship(r.id)) is r

def test_expunge(m):
    n1 = TNode()
    n2 = TNode()
    r = n1.trel_out.append(n2)
    assert r in m.session.relmap
    assert r in n1.trel_out.rels()
    assert r in n2.trel_in.rels()
    assert n1 in m.session.phantomnodes
    assert n2 in m.session.phantomnodes

    r.expunge()
    assert r not in m.session.relmap
    assert r not in n1.trel_out.rels()
    assert r not in n2.trel_in.rels()
    assert n1 in m.session.phantomnodes
    assert n2 in m.session.phantomnodes

    r = n1.trel_out.append(n2)
    n2.expunge()
    assert n2 not in m.session.phantomnodes
    assert r not in m.session.relmap
    assert r not in n1.trel_out.rels()
    assert n1 in m.session.phantomnodes

    n1.expunge()
    assert m.session.count == 0
    assert m.session.new == 0
    assert m.session.dirty == 0
    assert not m.session.is_dirty()
    assert len(m.session.nodes) == 0
    assert len(m.session.phantomnodes) == 0
    assert len(m.session.relmap) == 0
    assert len(m.session.propmap) == 0

def test_rollback(m):
    n1 = TNode()
    n2 = TNode()
    r1 = n1.trel_out.append(n2)
    m.session.commit()
    n3 = TNode()
    n4 = TNode()
    r2 = n3.trel_out.append(n4)
    n1.string = "test"
    r1.string = "test"
    r3 = n1.trel_out.append(n3)

    m.session.rollback()
    assert not m.session.is_dirty()
    assert n1 in m.session.nodes.values()
    assert not n1.is_dirty()
    assert n1.string is None
    assert n2 in m.session.nodes.values()
    assert not n2.is_dirty()
    assert r1 in m.session.relmap
    assert not r1.is_dirty()
    assert r1.string is None
    assert n3 not in m.session.phantomnodes
    assert n4 not in m.session.phantomnodes
    assert r2 not in m.session.relmap
    assert r3 not in m.session.relmap
    assert m.session.count == 3

def test_commit(m):
    from py2neo import neo4j

    n1 = TNode()
    n2 = TNode()
    r = n1.trel_out.append(n2)
    assert m.session.is_dirty()
    assert len(m.session.batch) == 0
    assert not m.session.committing
    assert n1._entity == None
    assert n1.id == None
    assert n2._entity == None
    assert n2.id == None
    assert r._entity == None
    assert r.id == None

    m.session.commit()
    assert not m.session.is_dirty()
    assert len(m.session.batch) == 0
    assert not m.session.committing
    assert isinstance(n1._entity, neo4j.Node)
    assert isinstance(n1.id, int)
    assert isinstance(n2._entity, neo4j.Node)
    assert isinstance(n2.id, int)
    assert isinstance(r._entity, neo4j.Relationship)
    assert isinstance(r.id, int)

def test_threadsafe(m):
    # initial state
    n1 = TNode()
    m.session.commit()
    n1.string = "test"
    n2 = TNode()
    n1.trel_out.append(n2)
    assert m.session.count == 3
    assert m.session.new == 2
    assert m.session.dirty == 1
    assert m.session.is_dirty()
    assert len(m.session.nodes) == 1
    assert len(m.session.phantomnodes) == 1
    assert len(m.session.relmap) == 1
    assert len(m.session.propmap) == 1
    
    # verify that subthread has separate session
    def test(q, m):
        try:
            assert m.session.count == 0
            assert m.session.new == 0
            assert m.session.dirty == 0
            assert not m.session.is_dirty()
            assert len(m.session.nodes) == 0
            assert len(m.session.phantomnodes) == 0
            assert len(m.session.relmap) == 0
            assert len(m.session.propmap) == 0
        except Exception as e:
            q.put(e)
        finally:
            m.session.clear()
    q = Queue()
    t = Thread(target=test, args=(q, m))
    t.start()
    t.join()
    if not q.empty():
        raise q.get()

    # verify subthread's m.session.clear() has not affected state
    assert m.session.count == 3
    assert m.session.new == 2
    assert m.session.dirty == 1
    assert m.session.is_dirty()
    assert len(m.session.nodes) == 1
    assert len(m.session.phantomnodes) == 1
    assert len(m.session.relmap) == 1
    assert len(m.session.propmap) == 1
