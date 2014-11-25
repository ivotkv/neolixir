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
        self.phantom_nodes = {}
        self.callbacks = []
        self.resubmit = False

    def clear(self):
        self.jobs = []
        self.phantom_nodes.clear()
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
                super(WriteBatch, self).create(py2neo.node(item.get_abstract()))
                self.phantom_nodes[item] = self.last

                def callback(item, metadata, response):
                    item._entity = response
                    item.properties.set_dirty(False)
                    metadata.session.phantomnodes.discard(item)
                    metadata.session.add(item)

                self.job_callback(callback, item, self.metadata)
                super(WriteBatch, self).create(py2neo.rel(self.last, "__instance_of__", item.classnode))

            elif isinstance(item, Relationship):
                abstract = [
                    self.phantom_nodes[item.start] if item.start.is_phantom() else item.start._entity,
                    item.type,
                    self.phantom_nodes[item.end] if item.end.is_phantom() else item.end._entity,
                    super(Relationship, item).get_abstract()
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
                    q = "start n=node({n_id}) "
                    q += "match n-[rels*1]-() foreach(rel in rels: delete rel) "
                    q += "delete n"
                    self.cypher(q, params={'n_id': item.id}, automap=False)
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
            return self.index(index, key, value, cls(value=None, **item))

        elif isinstance(item, Node):
            cls = item.__class__

            if item.is_phantom():
                self.get_or_create_in_index(neo4j.Node, index.index, key, value, item.get_abstract())
                self.phantom_nodes[item] = self.last

                def callback(self, job, cls, item, response):
                    query = """
                        start n=node({n_id}), c=node({c_id})
                        where not n-[:__instance_of__]->()
                        create unique n-[r:__instance_of__]->c
                        return r
                    """
                    params = {
                        'n_id': response.id,
                        'c_id': cls.classnode.id
                    }

                    if self.metadata.session.committing:
                        self.cypher(query, params=params, automap=False)

                        def callback2(cls, item, response1, response2):
                            if len(response2) > 0:
                                item.set_entity(response1)
                                return item
                            else:
                                item.expunge()
                                return cls(response1)

                        self.job_callback(callback2, cls, item, response)

                        for callback in job.callbacks[1:]:
                            self.jobs[-1].callbacks.append(callback)

                        self.resubmit = True
                        return False

                    else:
                        if len(self.metadata.cypher(query, params=params, automap=False)) > 0:
                            item.set_entity(response)
                            return item
                        else:
                            item.expunge()
                            return cls(response)

                self.job_callback(callback, self, self.jobs[-1], cls, item)

            else:
                self.get_or_add_to_index(neo4j.Node, index.index, key, value, item._entity)

                def callback(cls, item, response):
                    if item.id == response.id:
                        return item
                    else:
                        return cls(response)

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
