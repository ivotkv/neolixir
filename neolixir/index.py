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
from metadata import metadata as m
from exc import *
from entity import Entity
from node import Node
from relationship import Relationship

__all__ = ['NodeIndex', 'RelationshipIndex']

class Index(object):

    def __init__(self, type, name, config=None):
        self.type = type
        self.name = name
        self.config = config

    @property
    def index(self):
        try:
            return self._index
        except AttributeError:
            self._index = m.legacy.get_or_create_index(self.type, self.name, self.config)
            return self._index

    def clear(self):
        try:
            m.legacy.delete_index(self.type, self.name)
        except LookupError:
            pass
        try:
            delattr(self, '_index')
        except AttributeError:
            pass

    def add(self, key, value, entity, if_none=False):
        if isinstance(entity, Entity):
            entity = entity._entity
        func = self.index.add_if_none if if_none else self.index.add
        return func(unicode(key), unicode(value), entity) is not None

    def get(self, key, value=None, abstract=None):
        if value is None:
            return self.index.query("{0}:*".format(key))
        elif abstract is None:
            return self.index.get(unicode(key), unicode(value))
        else:
            return self.index.get_or_create(unicode(key), unicode(value), abstract)

    def query(self, query):
        return self.index.query(query)

    def remove(self, key=None, value=None, entity=None):
        if isinstance(entity, Entity):
            entity = entity._entity
        self.index.remove(unicode(key), unicode(value), entity)

class NodeIndex(Index):

    def __init__(self, name, config=None, cls=None):
        super(NodeIndex, self).__init__(neo4j.Node, name, config)
        self.cls = cls

    def get(self, key, value=None, item=None):
        if isinstance(item, dict):
            if self.cls:
                node = self.cls.get(value=None, **item)
            else:
                node = Node.get(value=None, **item)
            return self.get(key, value, node)
        elif isinstance(item, Node):
            if item.is_phantom():
                n = super(NodeIndex, self).get(key, value, item.get_abstract(exclude_null=True))
                if len(n.labels) == 0:
                    n.labels.update(item.clslabels)
                    n.push()
                    item.set_entity(n)
                    return item
                else:
                    item.expunge()
                    return Node.get(n)
            else:
                if self.add(key, value, item, if_none=True):
                    return item
                else:
                    return Node.get(super(NodeIndex, self).get(key, value)[0])
        else:
            return map(Node.get, super(NodeIndex, self).get(key, value))

    def query(self, query):
        return map(Node.get, super(NodeIndex, self).query(query))

class RelationshipIndex(Index):

    def __init__(self, name, config=None):
        super(RelationshipIndex, self).__init__(neo4j.Relationship, name, config)
