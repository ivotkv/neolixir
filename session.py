import threading
from itertools import chain
from py2neo import neo4j

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
        elif isinstance(entity._entity, neo4j.Node):
            self.nodes[entity.id] = entity
        elif isinstance(entity._entity, neo4j.Relationship):
            self.relationships[entity.id] = entity

    def get_entity(self, entity):
        if isinstance(entity, neo4j.Node):
            return self.nodes.get(entity.id)
        elif isinstance(entity, neo4j.Relationship):
            return self.relationships.get(entity.id)
        return None

    def expunge(self, entity):
        if entity.is_phantom():
            self.phantoms.remove(entity)
        elif isinstance(entity._entity, neo4j.Node):
            del self.nodes[entity.id]
        elif isinstance(entity._entity, neo4j.Relationship):
            del self.relationships[entity.id]

    def rollback(self):
        for entity in chain(self.nodes.values(), self.relationships.values()):
            entity.rollback()
        self.clear()

    def commit(self):
        # TODO Batch-ify
        from relationship import Relationship
        phantom_relationships = []
        while self.phantoms:
            entity = self.phantoms.pop()
            if isinstance(entity, Relationship):
                phantom_relationships.append(entity)
            else:
                entity.save()
        for entity in chain(self.nodes.values(), self.relationships.values()):
            entity.save()
        for entity in phantom_relationships:
            entity.save()
