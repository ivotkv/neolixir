import threading
from itertools import chain
from py2neo.neo4j import Node, Relationship

class Session(object):

    def __init__(self, metadata=None):
        self._metadata = metadata
        self.clear()

    def clear(self):
        self._threadlocal = threading.local()
        self._threadlocal.nodes = {}
        self._threadlocal.relationships = {}
        self._threadlocal.phantoms = set()

    @property
    def nodes(self):
        return self._threadlocal.nodes

    @property
    def relationships(self):
        return self._threadlocal.relationships

    @property
    def phantoms(self):
        return self._threadlocal.phantoms

    @property
    def count(self):
        return len(self.nodes) + len(self.relationships) + len(self.phantoms)

    @property
    def new(self):
        return len(self.phantoms)

    @property
    def dirty(self):
        return sum((1 for x in chain(self.nodes.values(), self.relationships.values()) if x.is_dirty()))

    def is_dirty(self):
        return self.new + self.dirty > 0

    def add_entity(self, entity):
        if entity.is_phantom():
            self.phantoms.add(entity)
        elif isinstance(entity._entity, Node):
            self.nodes[entity.id] = entity
        elif isinstance(entity._entity, Relationship):
            self.relationships[entity.id] = entity

    def get_entity(self, entity):
        if isinstance(entity, Node):
            return self.nodes.get(entity.id)
        elif isinstance(entity, Relationship):
            return self.relationships.get(entity.id)
        return None

    def rollback(self):
        for entity in chain(self.nodes.values(), self.relationships.values()):
            entity.rollback()
        self.clear()

    def commit(self):
        # TODO Batch-ify
        while self.phantoms:
            self.phantoms.pop().save()
        for entity in chain(self.nodes.values(), self.relationships.values()):
            entity.save()
