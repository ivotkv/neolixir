from py2neo import neo4j
from entity import Entity
from metadata import metadata as m
from node import Node

__all__ = ['Relationship']

class Relationship(Entity):

    def __new__(cls, value=None, **properties):
        if isinstance(value, int):
            value = m.engine.get_relationship(value)
        elif isinstance(value, tuple):
            value = (Node.get(value[0]), value[1], Node.get(value[2]))
            if value[0] is None:
                raise ValueError("start node not found!")
            if value[2] is None:
                raise ValueError("end node not found!")
            if not value[0].is_phantom() and not value[2].is_phantom():
                existing = value[0]._entity.get_relationships_with(value[2]._entity, 1, value[1])
                if len(existing) > 0:
                    value = existing[0]
        return super(Relationship, cls).__new__(cls, value, **properties)

    def __init__(self, value=None, **properties):
        if not self._initialized:
            if isinstance(value, tuple):
                self._start = Node.get(value[0])
                self._type = value[1]
                self._end = Node.get(value[2])
            super(Relationship, self).__init__(value, **properties)

    @property
    def start(self):
        return Node.get(self._entity.start_node) if self._entity is not None else self._start

    @property
    def end(self):
        return Node.get(self._entity.end_node) if self._entity is not None else self._end

    @property
    def type(self):
        return self._entity.type if self._entity is not None else self._type

    @property
    def tuple(self):
        return (self.start, self.type, self.end)

    def __repr__(self):
        return "<{0} (0x{1:x}): ({2})-[{3}:{4} {5}]->({6})>".format(self.__class__.__name__, id(self), self.start.id, self.id, self.type, self.properties, self.end.id)

    @classmethod
    def get(cls, value):
        if isinstance(value, cls):
            return value
        elif isinstance(value, (int, tuple)):
            return cls(value)
        else:
            return None

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

class RelationshipDict(dict):

    def __init__(self, direction):
        self.direction = direction

    def add(self, rel):
        pass

    def remove(self, rel):
        pass

    def get(self, item):
        if isinstance(item, int):
            if not self.has_key(int):
                return self.setdefault(item, RelationshipList(item)) 
        elif isinstance(item, Node):
            pass
        else:
            raise KeyError('unexpected key type')

class RelationshipMapper(object):

    def __init__(self):
        self._ids = {}
        self._phantoms = set()
        self._tuples = {}
        self.start = RelationshipDict('OUT')
        self.end = RelationshipDict('IN')

    def clear(self):
        self._ids.clear()
        self._phantoms.clear()
        self._tuples.clear()
        self.start.clear()
        self.end.clear()

    def add(self, rel):
        assert isinstance(rel, Relationship)
        if rel.id is not None:
            self._phantoms.discard(rel)
            self._ids[rel.id] = rel
        else:
            self._phantoms.add(rel)
        self._tuples[rel.tuple] = rel
        self.start.add(rel)
        self.end.add(rel)

    def remove(self, rel):
        assert isinstance(rel, Relationship)
        self._ids.pop(rel.id, None)
        self._phantoms.discard(rel)
        self._tuples.pop(rel.tuple, None)
        self.start.remove(rel)
        self.end.remove(rel)

    def get(self, value):
        if isinstance(value, int):
            return self._ids.get(value)
        elif isinstance(value, neo4j.Relationship):
            return self._ids.get(value.id)
        elif isinstance(value, tuple):
            return self._tuples.get(value)
        else:
            return None

    def __len__(self):
        return len(self._tuples)

    def __iter__(self):
        return self._tuples.itervalues()

    def itervalues(self):
        return self._tuples.itervalues()

    def values(self):
        return self._tuples.values()

    def iterphantoms(self):
        return iter(self._phantoms)

    def phantoms(self):
        return list(self._phantoms)

    def iterpersisted(self):
        return self._ids.itervalues()

    def persisted(self):
        return self._ids.values()

    def load_node_rels(self, node):
        if not node.is_phantom():
            for row in m.cypher("start n=node({0}) match n-[r]-() return r".format(node.id)):
                if row[0].type not in ('INSTANCE_OF', 'EXTENDS'):
                    self.add(Relationship(row[0]))
