from itertools import ifilter, imap
from py2neo import neo4j
from entity import Entity
from metadata import metadata as m
from node import Node

__all__ = ['Relationship']

class Relationship(Entity):

    def __new__(cls, value, **properties):
        if isinstance(value, int):
            value = m.engine.get_relationship(value)
        elif isinstance(value, tuple):
            value = (Node(value[0]), value[1], Node(value[2]))
            if value[0] is None:
                raise ValueError("start node not found!")
            if value[2] is None:
                raise ValueError("end node not found!")
            if not value[0].is_phantom() and not value[2].is_phantom():
                existing = value[0]._entity.get_relationships_with(value[2]._entity, 1, value[1])
                if len(existing) > 0:
                    value = existing[0]
        elif not isinstance(value, (cls, neo4j.Relationship)):
            raise ValueError("Relationship can only be instantiated by id, entity or tuple")
        return super(Relationship, cls).__new__(cls, value, **properties)

    def __init__(self, value=None, **properties):
        if not self._initialized:
            if self._entity is None and isinstance(value, tuple):
                self._start = Node(value[0])
                self._type = value[1]
                self._end = Node(value[2])
            super(Relationship, self).__init__(value, **properties)

    def __repr__(self):
        return "<{0} (0x{1:x}): ({2})-[{3}:{4} {5}]->({6})>".format(self.__class__.__name__, id(self), self.start.id, self.id, self.type, self.properties, self.end.id)

    @property
    def start(self):
        return Node(self._entity.start_node) if self._entity is not None else self._start

    @property
    def end(self):
        return Node(self._entity.end_node) if self._entity is not None else self._end

    @property
    def type(self):
        return self._entity.type if self._entity is not None else self._type

    @property
    def tuple(self):
        return (self.start, self.type, self.end)

    def get_abstract(self):
        return (self.start._entity, self.type, self.end._entity, super(Relationship, self).get_abstract())

    @classmethod
    def get(cls, value):
        if isinstance(value, cls):
            return value
        elif isinstance(value, (int, tuple)):
            return cls(value)
        else:
            return None

    def save(self):
        if self.is_deleted():
            if not self.is_phantom():
                self._entity.delete()
                self.expunge()
        elif self.is_phantom():
            if self.start is None or self.start.is_phantom() or \
                self.end is None or self.end.is_phantom():
                return False
            self._entity = m.engine.create(self.get_abstract())[0]
            m.session.add_entity(self)
        elif self.is_dirty():
            self.properties.save()
        return True

class RelationshipMapper(object):

    def __init__(self):
        self._ids = {}
        self._phantoms = set()
        self._tuples = {}
        self.start = {}
        self.end = {}

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
        self.start.setdefault(rel.start, set()).add(rel)
        self.end.setdefault(rel.end, set()).add(rel)

    def remove(self, rel):
        assert isinstance(rel, Relationship)
        self._ids.pop(rel.id, None)
        self._phantoms.discard(rel)
        self._tuples.pop(rel.tuple, None)
        self.start.setdefault(rel.start, set()).discard(rel)
        self.end.setdefault(rel.end, set()).discard(rel)

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

    def rollback(self):
        while len(self._phantoms) > 0:
            rel = self._phantoms.pop()
            self._tuples.pop(rel.tuple, None)
            self.start.setdefault(rel.start, set()).discard(rel)
            self.end.setdefault(rel.end, set()).discard(rel)
        for rel in self.iterpersisted():
            rel.rollback()

    def load_node_rels(self, node):
        if not node.is_phantom():
            for row in m.cypher("start n=node({0}) match n-[r]-() return r".format(node.id)):
                if row[0].type not in ('INSTANCE_OF', 'EXTENDS'):
                    self.add(Relationship(row[0]))

class RelationshipFilter(object):

    def __init__(self, owner, direction=None, type=None):
        self.map = m.session.relmap
        self.owner = owner
        self.direction = str(direction).upper()
        self.type = type

    def reload(self):
        self.map.load_node_rels(self.owner)

    @property
    def data(self):
        if self.direction == 'OUT':
            return self.map.start.setdefault(self.owner, set())
        elif self.direction == 'IN':
            return self.map.end.setdefault(self.owner, set())
        else:
            outgoing = self.map.start.setdefault(self.owner, set())
            incoming = self.map.end.setdefault(self.owner, set())
            return outgoing.union(incoming)

    def filterfunc(self, rel):
        if self.owner.is_deleted() != rel.is_deleted():
            return False
        else:
            return self.type is None or rel.type == self.type

    def nodefunc(self, rel):
        return rel.end if rel.start is self.owner else rel.start

    def relfunc(self, value):
        from relationship import Relationship
        if isinstance(value, Relationship):
            return value
        elif value is not None and self.direction in ('IN', 'OUT') and self.type is not None:
            from node import Node
            other = Node(value)
            if other is not None:
                if self.direction == 'OUT':
                    return Relationship((self.owner, self.type, other))
                else:
                    return Relationship((other, self.type, self.owner))
            else:
                raise ValueError("could not find other Node")
        else:
            raise ValueError("value could not be converted to Relationship")

    def __iter__(self):
        return ifilter(self.filterfunc, self.data)

    def __len__(self):
        return sum((1 for item in iter(self)))

    def __repr__(self):
        return "[{0}]".format(", ".join(imap(repr, iter(self))))

    def iternodes(self):
        return imap(self.nodefunc, iter(self))

    def nodes(self):
        return list(self.iternodes())

    def add(self, value):
        rel = self.relfunc(value)
        if rel.is_deleted():
            rel.undelete()

    @property
    def append(self):
        return self.add

    def remove(self, value):
        rel = self.relfunc(value)
        if rel in self:
            rel.delete()
