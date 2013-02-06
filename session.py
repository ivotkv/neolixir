import threading
from itertools import chain
from py2neo import neo4j

class Session(object):

    def __init__(self, metadata=None):
        self._threadlocal = threading.local()
        self._metadata = metadata

    def clear(self):
        self.nodes.clear()
        self.relationships.clear()
        self.relationship_tuples.clear()
        self.relmap.clear()
        self.phantoms.clear()

    @property
    def nodes(self):
        try:
            return self._threadlocal.nodes
        except AttributeError:
            self._threadlocal.nodes = {}
            return self._threadlocal.nodes

    @property
    def relationships(self):
        try:
            return self._threadlocal.relationships
        except AttributeError:
            self._threadlocal.relationships = {}
            return self._threadlocal.relationships

    @property
    def relationship_tuples(self):
        try:
            return self._threadlocal.relationship_tuples
        except AttributeError:
            self._threadlocal.relationship_tuples = {}
            return self._threadlocal.relationship_tuples

    @property
    def relmap(self):
        try:
            return self._threadlocal.relmap
        except AttributeError:
            from relationship import RelationshipMapper
            self._threadlocal.relmap = RelationshipMapper()
            return self._threadlocal.relmap

    @property
    def phantoms(self):
        try:
            return self._threadlocal.phantoms
        except AttributeError:
            self._threadlocal.phantoms = set()
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
        from relationship import Relationship
        if isinstance(entity, Relationship):
            self.relationship_tuples[entity.tuple] = entity
            self.relmap.add(entity)

    def get_entity(self, value):
        if isinstance(value, neo4j.Node):
            return self.nodes.get(value.id)
        elif isinstance(value, neo4j.Relationship):
            return self.relationships.get(value.id)
        elif isinstance(value, tuple):
            return self.relationship_tuples.get(value)
        return None

    def expunge(self, entity):
        if entity.is_phantom():
            self.phantoms.remove(entity)
        elif isinstance(entity._entity, neo4j.Node):
            del self.nodes[entity.id]
        elif isinstance(entity._entity, neo4j.Relationship):
            del self.relationships[entity.id]
        from relationship import Relationship
        if isinstance(entity, Relationship):
            del self.relationship_tuples[entity.tuple]
            self.relmap.remove(entity)

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
