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

import functools
from collections import Iterable
from utils import classproperty
import overrides
import py2neo
from py2neo import neo4j
from py2neo.batch import CypherJob
from py2neo.legacy.batch import LegacyWriteBatch
from node import Node
from relationship import Relationship

class WriteBatch(LegacyWriteBatch):

    def __init__(self, graph_db, metadata):
        super(WriteBatch, self).__init__(graph_db)
        self.metadata = metadata
        self.callbacks = []
        self.resubmit = False

    def clear(self):
        self.jobs = []
        self.callbacks = []

    def callback(self, func, *args):
        if args:
            self.callbacks.append(functools.partial(func, *args))
        else:
            self.callbacks.append(func)

    def job_callback(self, func, *args):
        if not hasattr(self.jobs[-1], 'callbacks'):
            self.jobs[-1].callbacks = []

        if args:
            self.jobs[-1].callbacks.append(functools.partial(func, *args))
        else:
            self.jobs[-1].callbacks.append(func)

    @property
    def last(self):
        return len(self.jobs) - 1

    def create(self, *items):
        for item in items:
            if isinstance(item, Node):
                self.cypher("""
                    create (n:{0} {{propmap}})
                    return n
                """.format(':'.join(item.clslabels)), params={
                    'propmap': item.get_abstract(exclude_null=True)
                }, automap=False)

                def callback(item, metadata, response):
                    item._entity = response[0][0]
                    item.properties.set_dirty(False)
                    metadata.session.phantomnodes.discard(item)
                    metadata.session.add(item)

                self.job_callback(callback, item, self.metadata)

            elif isinstance(item, Relationship):
                if item.start.is_phantom() or item.end.is_phantom():
                    raise NotImplementedError('creating a relationship in the same batch as its endpoints is not supported.')
                abstract = [
                    item.start._entity,
                    item.type,
                    item.end._entity,
                    super(Relationship, item).get_abstract(exclude_null=True)
                ]
                super(WriteBatch, self).create(py2neo.rel(*abstract))

                def callback(item, metadata, response):
                    item._entity = response
                    item.properties.set_dirty(False)
                    metadata.session.add(item)

                self.job_callback(callback, item, self.metadata)

            elif isinstance(item, dict):
                super(WriteBatch, self).create(py2neo.node(item))

            elif isinstance(item, Iterable):
                super(WriteBatch, self).create(py2neo.rel(*item))

            else:
                raise TypeError(u"cannot create entity from: {0}".format(item))

    def delete(self, *items):
        for item in items:
            if isinstance(item, Node):
                def callback(item, response):
                    item.expunge()
                    item._entity = None

                if not item.is_phantom():
                    self.cypher("""
                        start n=node({n_id})
                        optional match n-[rels*1]-() foreach(rel in rels | delete rel)
                        delete n
                    """, params={'n_id': item.id}, automap=False)
                    self.job_callback(callback, item)
                else:
                    self.callback(callback, item)

            elif isinstance(item, Relationship):
                def callback(item, response):
                    item.expunge()
                    item._entity = None

                if not (item.is_phantom() or \
                        item.start.is_deleted() or item.end.is_deleted()):
                    super(WriteBatch, self).delete(item._entity)
                    self.job_callback(callback, item)
                else:
                    self.callback(callback, item)

            elif isinstance(item, (neo4j.Node, neo4j.Relationship)):
                super(WriteBatch, self).delete(item)

            else:
                raise TypeError(u"cannot delete entity from: {0}".format(item))

    def index(self, index, key, value, item):
        if isinstance(item, dict):
            cls = index.cls or Node
            return self.index(index, key, value, cls.get(value=None, **item))

        elif isinstance(item, Node):
            cls = item.__class__

            if item.is_phantom():
                self.get_or_create_in_index(neo4j.Node, index.index, key, value, item.get_abstract(exclude_null=True))

                def callback(self, job, cls, item, response):
                    query = """
                        start n=node({{n_id}})
                        with n, length(labels(n)) as c
                        set n:{0}
                        return c
                    """.format(':'.join(cls.clslabels))
                    params = {
                        'n_id': response.id
                    }

                    if self.metadata.session.committing:
                        self.cypher(query, params=params, automap=False)

                        def callback2(cls, item, response1, response2):
                            if response2[0][0] == 0:
                                item.set_entity(response1)
                                return item
                            else:
                                item.expunge()
                                return cls.get(response1)

                        self.job_callback(callback2, cls, item, response)

                        for callback in job.callbacks[1:]:
                            self.jobs[-1].callbacks.append(callback)

                        self.resubmit = True
                        return False

                    else:
                        if self.metadata.cypher(query, params=params, automap=False)[0][0] == 0:
                            item.set_entity(response)
                            return item
                        else:
                            item.expunge()
                            return cls.get(response)

                self.job_callback(callback, self, self.jobs[-1], cls, item)

            else:
                self.get_or_add_to_index(neo4j.Node, index.index, key, value, item._entity)

                def callback(cls, item, response):
                    if item.id == response.id:
                        return item
                    else:
                        return cls.get(response)

                self.job_callback(callback, cls, item)

        else:
            raise NotImplementedError("batch indexing not implemented for item type: {0}".format(item))

    def save(self, *entities):
        for entity in entities:
            if isinstance(entity, (Node, Relationship)):

                if entity.is_deleted():
                    self.delete(entity)

                elif entity.is_phantom():
                    self.create(entity)

                elif entity.is_dirty():
                    if isinstance(entity, Node):
                        self.set_properties(entity._entity, entity.get_abstract())
                    else:
                        abstract = super(Relationship, entity).get_abstract()
                        self.set_properties(entity._entity, abstract)

                    def callback(entity, response):
                        entity.properties.set_dirty(False)

                    self.job_callback(callback, entity)

            else:
                raise TypeError(u"cannot save entity: {0}".format(entity))

    def cypher(self, query, params=None, automap=True):
        self.append(CypherJob(query, parameters=params))
        self.jobs[-1].automap = automap

    def query(self, query, automap=True):
        self.cypher(query.string, params=query.params, automap=automap)

    def submit(self, automap=True):
        jobs = self.jobs
        callbacks = self.callbacks
        responses = super(WriteBatch, self).submit() if len(jobs) > 0 else []
        self.clear()

        results = []
        for idx, response in enumerate(responses):
            job = jobs[idx]

            if hasattr(job, 'automap'):
                response = [list(record) for record in response]
                if automap and job.automap:
                    response = self.metadata.automap(response, mapRels=False)
                    response = self.metadata.automap(response, mapRels=True)

            if hasattr(job, 'callbacks'):
                for callback in job.callbacks:
                    output = callback(response)
                    if output is False:
                        break
                    elif output is not None:
                        response = output

            results.append(response)

        if self.resubmit:
            self.resubmit = False
            self.submit(automap=automap)

        for callback in callbacks:
            output = callback(results)
            if output is False:
                break
            elif output is not None:
                results = output

        return results
