import re
from itertools import ifilter, imap
from py2neo import neo4j
from exc import *
from entity import Entity
from metadata import metadata as m
from node import Node

__all__ = ['Relationship']

class Relationship(Entity):

    __rel_type__ = None

    _typed_classes = {}

    def __new__(cls, value, **properties):
        if isinstance(value, basestring):
            # returns a typed "copy" of the class
            if cls.__rel_type__ is not None:
                raise TypeError("cannot change the type of a typed Relationship class: " + cls.__name__)
            key = cls.__name__ + ':' + value
            try:
                return cls._typed_classes[key]
            except KeyError:
                return cls._typed_classes.setdefault(key, type(cls.__name__, (cls, ), {'__rel_type__': value}))
        elif isinstance(value, int):
            value = m.engine.get_relationship(value)
        elif isinstance(value, tuple):
            value = (Node(value[0]), cls.__rel_type__ or value[1], Node(value[2]))
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
            if self._entity is None:
                if isinstance(value, tuple):
                    self._start = Node(value[0])
                    self._type = self.__rel_type__ or value[1]
                    self._end = Node(value[2])
                else:
                    raise ValueError("Relationship could not be initialized with value provided")
            elif self.__rel_type__ is not None and self._entity.type != self.__rel_type__:
                raise TypeError("entity type does not match class type")
            super(Relationship, self).__init__(value, **properties)

    def __repr__(self):
        return "<{0} (0x{1:x}): ({2})-[{3}:{4} {5}]->({6})>".format(self.__class__.__name__, id(self), self.start.id, self.id, self.type, self.properties, self.end.id)

    @property
    def start(self):
        try:
            return self._start
        except AttributeError:
            self._start = Node(self._entity.start_node)
            return self._start

    @property
    def end(self):
        try:
            return self._end
        except AttributeError:
            self._end = Node(self._entity.end_node)
            return self._start

    @property
    def type(self):
        try:
            return self._type
        except AttributeError:
            self._type = self.__rel_type__ or self._entity.type
            return self._type

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
                try:
                    self._entity.delete()
                except ResourceNotFound:
                    pass
                self.expunge()
                self._entity = None
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
            for row in m.cypher("start n=node({0}) match n-[r]-() return r".format(node.id), automap=False):
                if row[0].type != '__instance_of__':
                    self.add(Relationship(row[0]))

class RelationshipFilter(object):

    def __init__(self, owner, direction=None, type=None, cls=None, match=None):
        self.map = m.session.relmap
        self.owner = owner
        self.direction = str(direction).upper()
        self.type = getattr(cls, '__rel_type__', None) or type
        self.cls = cls or Relationship
        self.match = match

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
        elif self.type is None:
            return not self.match or re.match(self.match, rel.type)
        else:
            return rel.type == self.type or (self.match and re.match(self.match, rel.type))

    def nodefunc(self, rel):
        return rel.end if rel.start is self.owner else rel.start

    def relfunc(self, value):
        if isinstance(value, Relationship):
            return value
        elif value is not None and self.direction in ('IN', 'OUT') and self.type is not None:
            other = Node(value)
            if other is not None:
                if self.direction == 'OUT':
                    return self.cls((self.owner, self.type, other))
                else:
                    return self.cls((other, self.type, self.owner))
            else:
                raise ValueError("could not find other Node")
        else:
            raise ValueError("value could not be converted to Relationship")

    def __iter__(self):
        return ifilter(self.filterfunc, self.data)

    def __contains__(self, item):
        if isinstance(item, Relationship):
            return item in self.__iter__()
        else:
            return item in imap(self.nodefunc, self.__iter__())

    def __len__(self):
        return sum((1 for item in iter(self)))

    def __repr__(self):
        return "[{0}]".format(", ".join(imap(repr, iter(self))))

    def iternodes(self):
        return ((self.nodefunc(x), x) for x in self)

    def nodes(self):
        return dict(self.iternodes())

    def iterrels(self):
        return ((x, self.nodefunc(x)) for x in self)

    def rels(self):
        return dict(self.iterrels())

    def add(self, value):
        rel = self.relfunc(value)
        if rel.is_deleted():
            rel.undelete()

    def remove(self, value):
        rel = self.relfunc(value)
        if rel in self:
            rel.delete()
