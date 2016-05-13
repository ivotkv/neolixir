# -*- coding: utf-8 -*-
# 
# The MIT License (MIT)
# 
# Copyright (c) 2013 Ivaylo Tzvetkov, ChallengeU
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 

import overrides
from py2neo import neo4j
from exc import *
from metadata import metadata as m
from entity import Entity
from node import Node
from dummy import DummyNode, DummyRelationship

__all__ = ['Relationship']

class Relationship(Entity):

    __rel_type__ = None

    __sort_cmp__ = None
    __sort_key__ = None

    _typed_classes = {}

    @classmethod
    def get(cls, value, **properties):
        if not isinstance(value, (DummyRelationship, neo4j.Relationship, cls)):
            if isinstance(value, int):
                try:
                    value = m.graph.relationship(value)
                except ValueError as e:
                    if str(e).find('not found') > 0:
                        raise EntityNotFoundException(str(e))
                    raise e
            elif isinstance(value, tuple):
                value = (cls.node(value[0]), cls.__rel_type__ or value[1], cls.node(value[2]))
                if value[0] is None:
                    raise ValueError("start node not found!")
                if value[2] is None:
                    raise ValueError("end node not found!")
            else:
                raise ValueError(u"unexpected value for Relationship: {0}".format(value))
        return super(Relationship, cls).get(value=value, **properties)

    def __new__(cls, entity=None, **properties):
        if isinstance(entity, basestring):
            # returns a typed "copy" of the class
            if cls.__rel_type__ is not None:
                raise TypeError("cannot change the type of a typed Relationship class: " + cls.__name__)
            key = cls.__name__ + ':' + entity
            try:
                return cls._typed_classes[key]
            except KeyError:
                return cls._typed_classes.setdefault(key, type(cls.__name__, (cls, ), {'__rel_type__': entity}))
        else:
            return super(Relationship, cls).__new__(cls)

    def __init__(self, entity=None, **properties):
        if isinstance(entity, tuple):
            self._start = self.node(entity[0])
            self._type = self.__rel_type__ or entity[1]
            self._end = self.node(entity[2])
        elif not isinstance(entity, (DummyRelationship, neo4j.Relationship)):
            raise ValueError(u"cannot initialize Relationship from entity: {0}".format(entity))
        super(Relationship, self).__init__(entity=entity, **properties)
        if self.__rel_type__ is not None and self.type != self.__rel_type__:
            raise TypeError("entity type does not match class type")
        if self.start.is_deleted() or self.end.is_deleted():
            self.delete()

    def __repr__(self):
        return "<{0} (0x{1:x}): ({2})-[{3}:{4}]->({5}) {6}>".format(self.__class__.__name__, id(self), self.start.id, self.id, self.type, self.end.id, self.properties)

    def __cmp__(self, other):
        if not isinstance(other, Relationship):
            return cmp(id(self), id(other))
        elif self.__sort_cmp__ is not None:
            return self.__sort_cmp__(self, other)
        elif self.__sort_key__ is not None:
            return cmp(self.__sort_key__(self), self.__sort_key__(other))
        else:
            if self._entity is not None or other._entity is not None:
                return cmp(self.id, other.id)
            else:
                return cmp(id(self), id(other))

    def __eq__(self, other):
        return self is other

    def __ne__(self, other):
        return self is not other

    @property
    def cls(self):
        if self.__class__.__rel_type__ is not None:
            return m.classes[self.__class__.__name__]
        else:
            return self.__class__

    @property
    def start(self):
        try:
            return self._start
        except AttributeError:
            self._start = self.node(self._entity.start_node)
            return self._start

    @property
    def end(self):
        try:
            return self._end
        except AttributeError:
            self._end = self.node(self._entity.end_node)
            return self._end

    @property
    def type(self):
        try:
            return self._type
        except AttributeError:
            self._type = self._entity.type
            return self._type

    @property
    def tuple(self):
        return (self.start, self.type, self.end)

    def other(self, node):
        if node is self.start:
            return self.end
        elif node is self.end:
            return self.start
        else:
            raise ValueError('value provided is not an end node of this relationship')

    def get_abstract(self, exclude_null=False):
        return (self.start._entity, self.type, self.end._entity,
                super(Relationship, self).get_abstract(exclude_null=exclude_null))

    @classmethod
    def node(cls, value):
        if isinstance(value, DummyNode) and len(value.properties) == 0:
            value = m.graph.node(value.id)
        return Node.get(value)

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
                    except EntityNotFoundException:
                        pass
                self.expunge()
                self._entity = None

            elif self.is_phantom():
                if self.start is None or self.start.is_phantom() or \
                    self.end is None or self.end.is_phantom():
                    return False
                self._entity = m.graph.create(self.get_abstract(exclude_null=True))[0]
                m.session.add(self)

            elif self.is_dirty():
                self.properties.save()

        return True
