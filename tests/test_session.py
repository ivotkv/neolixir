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

    n1.rel_out.append(n2)
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

def test_threadsafe(m):
    # initial state
    n1 = TNode()
    m.session.commit()
    n1.string = "test"
    n2 = TNode()
    n1.rel_out.append(n2)
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

def test_add(m):
    pass

def test_get(m):
    pass

def test_expunge(m):
    assert m.session.count == 0

    n1 = TNode()
    assert m.session.count == 1
    assert n1 in m.session.phantomnodes
    assert len(m.session.nodes) == 0

    n1.expunge()
    assert m.session.count == 0
    assert n1 not in m.session.phantomnodes
    assert len(m.session.nodes) == 0

def test_rollback(m):
    pass

def test_commit(m):
    pass
