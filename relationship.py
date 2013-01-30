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

class RelationshipList(list):

    def __init__(self, owner, direction, type):
        super(RelationshipList, self).__init__()
        self.owner = owner
        self.direction = direction
        self.type = type

    def from_node(self, node):
        if self.direction == 'OUT':
            return Relationship((self.owner, self.type, node))
        else:
            return Relationship((node, self.type, self.owner))

    @property
    def nodefunc(self):
        if self.direction == 'OUT':
            return lambda rel: rel.end
        else:
            return lambda rel: rel.start

    def iternodes(self):
        return (self.nodefunc(rel) for rel in self)

    def nodes(self):
        return [self.nodefunc(rel) for rel in self]

    def validate(self, value):
        if isinstance(value, Node):
            value = self.from_node(value)
        elif not isinstance(value, Relationship):
            raise ValueError("expected Relationship or Node")
        return value

    def __setitem__(self, key, value):
        value = self.validate(value)
        super(RelationshipList, self).__setitem__(key, value)

    def insert(self, index, value):
        value = self.validate(value)
        super(RelationshipList, self).insert(index, value)

    def append(self, value):
        value = self.validate(value)
        if value not in self:
            super(RelationshipList, self).append(value)

    def extend(self, list):
        super(RelationshipList, self).extend((v for v in (self.validate(v) for v in list) if v not in self))

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

    def setdefault(self, key):
        return super(RelationshipContainer, self).setdefault(key, RelationshipList(self.owner, *key.split(':')))

    def get(self, key):
        return self.setdefault(key)

    def add(self, rel):
        key = self.get_key(rel)
        self.setdefault(key).append(rel)

    def remove(self, rel):
        key = self.get_key(rel)
        if self.has_key(key):
            self[key].remove(rel)
