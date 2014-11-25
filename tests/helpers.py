from neolixir.relmap import RelView
from utils import *

def create_out_of_session(m, entity):

    assert entity.is_phantom()
    entity.expunge()

    @checked_thread
    def run(m, entity):
        m.session.add(entity)
        m.session.commit()
        return entity.id

    return run(m, entity)

def update_out_of_session(m, entity, properties=None):

    assert not entity.is_phantom()
    if properties == None:
        properties = entity.properties

    @checked_thread
    def run(m, entity, properties):
        entity = entity.__class__(entity.id)
        entity.properties.update(properties)
        m.session.commit()
        return m.session.dirty == 0

    return run(m, entity, properties)

def delete_out_of_session(m, entity):

    assert not entity.is_phantom()

    @checked_thread
    def run(m, entity):
        entity = entity.__class__(entity.id)
        entity.delete()
        m.session.commit()
        return entity not in m.session

    return run(m, entity)

def append_out_of_session(m, n1, relname, n2):

    assert not n1.is_phantom()
    assert isinstance(relname, basestring)
    assert isinstance(getattr(n1, relname, None), RelView)
    assert not n2.is_phantom()

    @checked_thread
    def run(m, n1, relname, n2):
        n1 = n1.__class__(n1.id)
        n2 = n2.__class__(n2.id)
        rel = getattr(n1, relname).append(n2)
        m.session.commit()
        return rel.id if rel else None

    return run(m, n1, relname, n2)

def remove_out_of_session(m, n1, relname, n2):

    assert not n1.is_phantom()
    assert isinstance(relname, basestring)
    assert isinstance(getattr(n1, relname, None), RelView)
    assert not n2.is_phantom()

    @checked_thread
    def run(m, n1, relname, n2):
        n1 = n1.__class__(n1.id)
        n2 = n2.__class__(n2.id)
        relview = getattr(n1, relname)
        if n2 in relview:
            count = len(relview)
            relview.remove(n2)
            m.session.commit()
            return len(relview) == count - 1
        else:
            return False

    return run(m, n1, relname, n2)
