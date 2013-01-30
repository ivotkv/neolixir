from py2neo import neo4j
from entity import Entity
from metadata import metadata as m
from node import Node

__all__ = ['Relationship']

class Relationship(Entity):

    def __new__(cls, entity_or_tuple=None, **properties):
        entity = entity_or_tuple if isinstance(entity_or_tuple, neo4j.Relationship) else None
        return super(Relationship, cls).__new__(cls, entity, **properties)

    def __init__(self, entity_or_tuple=None, **properties):
        if not self._initialized:
            if isinstance(entity_or_tuple, tuple):
                self._start = Node.get(entity_or_tuple[0])
                self._type = entity_or_tuple[1]
                self._end = Node.get(entity_or_tuple[2])
                entity = None
            elif isinstance(entity_or_tuple, neo4j.Relationship):
                self._start = None
                self._type = None
                self._end = None
                entity = entity_or_tuple
            else:
                raise ValueError("expected neo4j.Relationship or tuple")
            super(Relationship, self).__init__(entity, **properties)
            self.add_to_owners()

    @property
    def start(self):
        return Node.get(self._entity.start_node) if self._entity else self._start

    @property
    def end(self):
        return Node.get(self._entity.end_node) if self._entity else self._end

    @property
    def type(self):
        return self._entity.type if self._entity else self._type

    def __repr__(self):
        return "<{0} (0x{1:x}): {2}-[{3}:{4} {5}]->{6}>".format(self.__class__.__name__, id(self), self.start, self.id, self.type, self.properties, self.end)

    def add_to_owners(self):
        if self.start:
            self.start.relationships.add(self)
        if self.end:
            self.end.relationships.add(self)

    def save(self):
        if self.is_phantom():
            if self.start is None or self.start.is_phantom() or\
                self.end is None or self.end.is_phantom():
                return False
            self._entity = m.engine.create((self.start._entity, self.type, self.end._entity, self.properties))[0]
            m.session.add_entity(self)
            self.properties.reload()
        elif self.is_dirty():
            self.properties.save()
        return True

class RelationshipContainer(dict):

    def __init__(self, owner):
        super(RelationshipContainer, self).__init__()
        self.owner = owner

    def reload(self):
        for rel in (r for s in self.values() for r in s if r.is_phantom()):
            rel.expunge()
        self.clear()
        if not self.owner.is_phantom():
            for row in m.execute("start n=node({0}) match n-[r]-() return r".format(self.owner.id)):
                if row[0].type not in ('INSTANCE_OF', 'EXTENDS'):
                    self.add(Relationship(row[0]))

    def get_key(self, rel):
        return ('OUT:' if rel.start == self.owner else 'IN:') + rel.type

    def add(self, rel):
        key = self.get_key(rel)
        self.setdefault(key, set())
        self[key].add(rel)

    def remove(self, rel):
        key = self.get_key(rel)
        if self.has_key(key):
            self[key].remove(rel)
