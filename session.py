import threading
from itertools import chain
from py2neo import neo4j

class Session(object):

    def __init__(self, metadata=None):
        self._threadlocal = threading.local()
        self.metadata = metadata

    def clear(self):
        self.batch.clear()
        self.nodes.clear()
        self.phantomnodes.clear()
        self.relmap.clear()
        self.propmap.clear()

    @property
    def committing(self):
        try:
            return self._threadlocal.committing
        except AttributeError:
            self._threadlocal.committing = False
            return self._threadlocal.committing

    @committing.setter
    def committing(self, value):
        self._threadlocal.committing = value

    @property
    def batch(self):
        try:
            return self._threadlocal.batch
        except AttributeError:
            self._threadlocal.batch = self.metadata.batch()
            return self._threadlocal.batch

    @property
    def nodes(self):
        try:
            return self._threadlocal.nodes
        except AttributeError:
            self._threadlocal.nodes = {}
            return self._threadlocal.nodes

    @property
    def phantomnodes(self):
        try:
            return self._threadlocal.phantomnodes
        except AttributeError:
            self._threadlocal.phantomnodes = set()
            return self._threadlocal.phantomnodes

    @property
    def relmap(self):
        try:
            return self._threadlocal.relmap
        except AttributeError:
            from relmap import RelMap
            self._threadlocal.relmap = RelMap()
            return self._threadlocal.relmap

    @property
    def propmap(self):
        try:
            return self._threadlocal.propmap
        except AttributeError:
            from propmap import PropMap
            self._threadlocal.propmap = PropMap()
            return self._threadlocal.propmap

    def __len__(self):
        return self.count

    @property
    def count(self):
        return len(self.nodes) + len(self.phantomnodes) + len(self.relmap)

    @property
    def new(self):
        return len(self.phantomnodes) + len(self.relmap._phantoms)

    @property
    def dirty(self):
        return sum((1 for x in chain(self.nodes.itervalues(), self.relmap.iterpersisted()) if x.is_dirty()))

    def is_dirty(self):
        return self.new + self.dirty > 0

    def add(self, entity):
        from relationship import Relationship
        if isinstance(entity, Relationship):
            self.relmap.add(entity)
        else:
            if entity.is_phantom():
                self.phantomnodes.add(entity)
            else:
                self.phantomnodes.discard(entity)
                self.nodes[entity.id] = entity
        entity._session = self

    def get(self, value):
        if isinstance(value, neo4j.Node):
            return self.nodes.get(value.id)
        elif isinstance(value, neo4j.Relationship):
            return self.relmap.get(value)
        else:
            return None

    def expunge(self, entity):
        from relationship import Relationship
        if isinstance(entity, Relationship):
            self.relmap.remove(entity)
        else:
            for rel in list(self.relmap.node.get(entity, [])):
                self.expunge(rel)
            self.phantomnodes.discard(entity)
            self.nodes.pop(entity.id, None)
        self.propmap.remove(entity)
        entity._session = None

    def rollback(self):
        self.batch.clear()
        self.propmap.clear()
        self.relmap.rollback()
        self.phantomnodes.clear()
        for node in self.nodes.itervalues():
            node.rollback()

    def commit(self, batched=True):
        self.committing = True

        if batched:
            self.batch.clear()

            nodes = list(chain(self.phantomnodes, self.nodes.itervalues()))
            rels = list(self.relmap)

            self.batch.save(*nodes)
            self.batch.submit()

            self.batch.save(*rels)
            self.batch.submit()

        else:
            while len(self.phantomnodes) > 0:
                self.phantomnodes.pop().save()
            for entity in list(chain(self.nodes.itervalues(), self.relmap)):
                entity.save()

        self.committing = False
