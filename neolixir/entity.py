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
import py2neo
from py2neo import neo4j
from exc import *
from utils import classproperty
from metadata import metadata as m
from properties import Property, FieldDescriptor
from observable import Observable, ObservableMeta
from dummy import DummyEntity

__all__ = ['Entity']

class EntityMeta(ObservableMeta):

    def __init__(cls, name, bases, dict_):
        super(EntityMeta, cls).__init__(name, bases, dict_)

        # inherited labels
        cls._labels = cls._labels + (name,) if hasattr(cls, '_labels') else (name,)

        # inherited descriptors
        cls._descriptors = cls._descriptors.copy() if hasattr(cls, '_descriptors') else {}
        for base in bases:
            if hasattr(base, '_descriptors'):
                for k, v in base._descriptors.iteritems():
                    if k not in cls._descriptors:
                        cls._descriptors[k] = v

        # class-defined descriptors
        for k, v in dict_.iteritems():
            if isinstance(v, FieldDescriptor):
                cls._descriptors[k] = v
                v.name = k
        
        m.add(cls)

class Entity(Observable):

    """Base class for all Neolixir entities (Nodes and Relationships).
    
    Defines basic shared functionality and handles proper subclassing and 
    instance initialization, instance registration and descriptor setup.

    Should not be used directly, always use :class:`node.Node` or 
    :class:`relationship.Relationship` instead.

    :param value: A :class:`py2neo.neo4j.Node` or :class:`py2neo.neo4j.Relationship` instance, or None.
    :param \*\*properties: Keyword arguments will be used to initialize the entity's properties.
    :returns: An :class:`Entity` or a subclass thereof.
    
    """
    
    __metaclass__ = EntityMeta

    _deleted = False

    @classmethod
    def get(cls, value, **properties):
        if isinstance(value, cls):
            return value
        instance = m.session.get(value)
        if instance is not None:
            return instance
        elif isinstance(value, (DummyEntity, neo4j.Node, neo4j.Relationship)):
            try:
                loaded_properties = m.session.propmap.get_properties(value)
            except GraphError as e:
                if str(e).find('not found') > 0:
                    raise EntityNotFoundException(str(e))
                raise e
            valcls = m.classes.get(loaded_properties.get('__class__'))
            if not valcls or not issubclass(valcls, cls):
                raise TypeError("entity is not an instance of " + cls.__name__)
            return valcls(entity=value, **properties)
        else:
            return cls(entity=value, **properties)

    def __init__(self, entity=None, **properties):
        if isinstance(entity, (DummyEntity, neo4j.Node, neo4j.Relationship)):
            self._entity = entity
        else:
            self._entity = None
        for k, v in properties.iteritems():
            if k in self._descriptors:
                setattr(self, k, v)
            else:
                self.properties[k] = v
        m.session.add(self)
        if self.is_phantom():
            self.fire_event('create', self)

    def __copy__(self):
        # TODO: support copying?
        return self

    def __deepcopy__(self, memo):
        # TODO: support deepcopying?
        return self

    def _get_repr_data(self):
        return ["Id = {0}".format(self.id),
                "Descriptors = {0}".format(sorted(self.descriptors.keys())),
                "Properties = {0}".format(self.properties)]

    def __repr__(self):
        return "<{0} (0x{1:x}): \n{2}\n>".format(self.__class__.__name__, id(self),
                                                 "\n".join(self._get_repr_data()))

    @property
    def _entity(self):
        return self.__entity

    @_entity.setter
    def _entity(self, value):
        self.__entity = value
        if value is not None:
            value.properties

    @property
    def cls(self):
        return self.__class__

    @property
    def id(self):
        return getattr(self._entity, 'id', None)

    @property
    def descriptors(self):
        return self._descriptors

    @property
    def properties(self):
        try:
            return self._properties
        except AttributeError:
            self._properties = m.session.propmap.get_properties(self)
            self._properties.owner = self
            return self._properties

    def get_properties(self):
        data = {}
        for k, v in self._descriptors.iteritems():
            if isinstance(v, Property):
                data[k] = getattr(self, k)
        for k, v in self.properties.iteritems():
            data.setdefault(k, v)
        return data

    def set_properties(self, data):
        for k, v in data.iteritems():
            if k in self._descriptors:
                setattr(self, k, v)
            else:
                self.properties[k] = v

    def get_abstract(self, exclude_null=False):
        self.properties.sanitize()
        if exclude_null:
            return {k: v for k, v in self.properties.iteritems() if v is not None}
        else:
            return self.properties

    def set_entity(self, entity):
        if self._entity is None:
            self._entity = entity
            try:
                del self._properties
            except AttributeError:
                pass
            if getattr(self, '_session', None):
                self._session.add(self)
            return True
        else:
            return False

    def is_phantom(self):
        return self._entity is None

    def is_deleted(self):
        return self._deleted

    def is_dirty(self):
        if self.is_deleted():
            return True
        elif not hasattr(self, '_properties'):
            return False
        else:
            return self.properties.is_dirty()

    def is_expunged(self):
        return getattr(self, '_session', None) is None

    def expunge(self):
        if getattr(self, '_session', None):
            self._session.expunge(self)
            self._session = None

    def rollback(self):
        self._deleted = False
        try:
            del self._properties
        except AttributeError:
            pass

    def delete(self):
        self._deleted = True
        if self.is_phantom():
            self.expunge()
        else:
            self.fire_event('delete', self)

    def save(self, batch=None):
        raise NotImplementedError("cannot save through generic Entity class")

    def has_observer(self, event, target):
        return super(Entity, self).has_observer(event, target) or \
               (event == 'change' and super(Entity, self).has_observer('update', target)) or \
               (event in ('change', 'append', 'remove') and target in self.descriptors and \
                self.descriptors[target].has_observer(event, target))

    def fire_event(self, event, target, *args):
        if not (self.is_expunged() and event != 'delete_committed'):
            super(Entity, self).fire_event(event, target, *args)
            if event == 'change':
                self.fire_event('update', self)
                if target in self.descriptors:
                    self.descriptors[target].fire_event(event, (self, target), *args)
            elif event in ('append', 'remove') and target in self.descriptors:
                self.descriptors[target].fire_event(event, (self, target), *args)
