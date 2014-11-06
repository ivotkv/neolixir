import overrides
from py2neo import neo4j
from exc import *
from metadata import metadata as m
from entity import Entity
from node import Node

__all__ = ['Relationship']

class Relationship(Entity):

    __rel_type__ = None

    __sort_cmp__ = None
    __sort_key__ = None

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
            try:
                value = m.graph.relationship(value)
            except ValueError as e:
                if str(e).find('not found') > 0:
                    raise ResourceNotFound(str(e))
                raise e
        elif isinstance(value, tuple):
            value = (Node(value[0]), cls.__rel_type__ or value[1], Node(value[2]))
            if value[0] is None:
                raise ValueError("start node not found!")
            if value[2] is None:
                raise ValueError("end node not found!")
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
            self.tuple # NOTE: the tuple needs to be inited for some reason - why??
            super(Relationship, self).__init__(value, **properties)

    def __repr__(self):
        return "<{0} (0x{1:x}): ({2})-[{3}:{4} {5}]->({6})>".format(self.__class__.__name__, id(self), self.start.id, self.id, self.type, self.properties, self.end.id)

    def __cmp__(self, other):
        if not isinstance(other, Relationship):
            return cmp(id(self), id(other))
        elif self.__sort_cmp__ is not None:
            return self.__sort_cmp__(self, other)
        elif self.__sort_key__ is not None:
            return cmp(self.__sort_key__(self), self.__sort_key__(other))
        else:
            if self.id is not None:
                return cmp(self.id, other.id)
            else:
                return cmp(id(self), id(other))

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

    def rollback(self):
        if self.is_deleted() and getattr(self, '_relmap', None):
            self._deleted = False
            self._relmap.update(self)
        super(Relationship, self).rollback()

    def delete(self):
        super(Relationship, self).delete()
        if getattr(self, '_relmap', None):
            self._relmap.update(self)

    def save(self, batch=None):
        if batch:
            batch.save(self)

        else:
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
                self._entity = m.graph.create(self.get_abstract())[0]
                m.session.add(self)

            elif self.is_dirty():
                self.properties.save()

        return True
