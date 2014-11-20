from Queue import Queue
from threading import Thread
from neolixir.relmap import RelView

def create_out_of_session(m, entity):

    assert entity.is_phantom()
    entity.expunge()

    def run(q, m, entity):
        m.session.add(entity)
        m.session.commit()
        q.put(entity.id)

    q = Queue()
    t = Thread(target=run, args=(q, m, entity))
    t.start()
    t.join()
    return q.get() if not q.empty() else None

def update_out_of_session(m, entity, properties=None):

    assert not entity.is_phantom()
    if properties == None:
        properties = entity.properties

    def run(q, m, entity, properties):
        entity = entity.__class__(entity.id)
        entity.properties.update(properties)
        m.session.commit()
        q.put(m.session.dirty == 0)

    q = Queue()
    t = Thread(target=run, args=(q, m, entity, properties))
    t.start()
    t.join()
    return q.get() if not q.empty() else None

def delete_out_of_session(m, entity):

    assert not entity.is_phantom()

    def run(q, m, entity):
        entity = entity.__class__(entity.id)
        entity.delete()
        m.session.commit()
        q.put(m.session.count == 0)

    q = Queue()
    t = Thread(target=run, args=(q, m, entity))
    t.start()
    t.join()
    return q.get() if not q.empty() else None

def append_out_of_session(m, n1, relname, n2):

    assert not n1.is_phantom()
    assert isinstance(relname, basestring)
    assert isinstance(getattr(n1, relname, None), RelView)
    assert not n2.is_phantom()

    def run(q, m, n1, relname, n2):
        n1 = n1.__class__(n1.id)
        n2 = n2.__class__(n2.id)
        rel = getattr(n1, relname).append(n2)
        m.session.commit()
        q.put(rel.id if rel else None)

    q = Queue()
    t = Thread(target=run, args=(q, m, n1, relname, n2))
    t.start()
    t.join()
    return q.get() if not q.empty() else None

def remove_out_of_session(m, n1, relname, n2):

    assert not n1.is_phantom()
    assert isinstance(relname, basestring)
    assert isinstance(getattr(n1, relname, None), RelView)
    assert not n2.is_phantom()

    def run(q, m, n1, relname, n2):
        n1 = n1.__class__(n1.id)
        n2 = n2.__class__(n2.id)
        relview = getattr(n1, relname)
        if n2 in relview:
            count = len(relview)
            relview.remove(n2)
            m.session.commit()
            q.put(len(relview) == count - 1)
        else:
            q.put(False)

    q = Queue()
    t = Thread(target=run, args=(q, m, n1, relname, n2))
    t.start()
    t.join()
    return q.get() if not q.empty() else None
