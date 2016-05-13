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
from utils import classproperty
from exc import *
from metadata import metadata as m
from entity import Entity
from query import Query
from dummy import DummyNode

__all__ = ['Node']

class Node(Entity):
    
    __query_cls__ = Query

    @classmethod
    def get(cls, value, **properties):
        if isinstance(value, int):
            try:
                value = m.graph.node(value)
            except ValueError as e:
                if str(e).find('not found') > 0:
                    raise EntityNotFoundException(str(e))
                raise e
        elif value is not None and not isinstance(value, (cls, DummyNode, neo4j.Node)):
            raise ValueError(u"unexpected value for Node: {0}".format(value))
        return super(Node, cls).get(value=value, **properties)

    def __init__(self, entity=None, **properties):
        if not (entity is None or isinstance(entity, (DummyNode, neo4j.Node))):
            raise ValueError(u"cannot initialize Node from entity: {0}".format(entity))
        self._relfilters = {}
        super(Node, self).__init__(entity=entity, **properties)

    @classproperty
    def clslabel(cls):
        return cls.__name__

    @classproperty
    def clslabels(cls):
        return cls._labels

    def relview(self, name):
        descriptor = getattr(self.__class__, name)
        return descriptor.get_relview(self)

    def delete(self):
        try:
            while True:
                m.session.relmap.node[self].pop().delete()
        except KeyError:
            pass
        super(Node, self).delete()

    def save(self, batch=None):
        if batch:
            batch.save(self)

        else:
            if self.is_deleted():
                if not self.is_phantom():
                    m.cypher("""
                        start n=node({n_id})
                        optional match n-[rels*1]-() foreach(rel in rels | delete rel)
                        delete n
                    """, params={'n_id': self.id})
                self.expunge()
                self._entity = None

            elif self.is_phantom():
                self._entity = m.graph.create(neo4j.Node(*self.clslabels, **self.get_abstract(exclude_null=True)))[0]
                m.session.add(self)

            elif self.is_dirty():
                self.properties.save()

        return True

    @classproperty
    def query(cls):
        return cls.__query_cls__.node(cls)

    @classmethod
    def get_by(cls, **kwargs):
        if 'id' in kwargs:
            try:
                return cls.get(kwargs['id'])
            except EntityNotFoundException:
                return None
        else:
            clauses = [u"instance.{0} = {1}".format(k, repr(v)) for k, v in kwargs.iteritems()]
            return cls.query.append('where {0}'.format(' and '.join(clauses))).first()
