import threading
import functools
from collections import Iterable
from utils import classproperty
from py2neo import neo4j, cypher

class Engine(object):

    def __init__(self, url='http://localhost:7474/db/data/', metadata=None):
        self._threadlocal = threading.local()
        self.metadata = metadata
        self.url = url

    @property
    def instance(self):
        try:
            return self._threadlocal.instance
        except AttributeError:
            self._threadlocal.instance = neo4j.GraphDatabaseService(self.url)
            return self._threadlocal.instance

    @classproperty
    def Node(cls):
        try:
            return cls._Node
        except AttributeError:
            from node import Node
            cls._Node = Node
            return cls._Node

    @classproperty
    def Relationship(cls):
        try:
            return cls._Relationship
        except AttributeError:
            from relationship import Relationship
            cls._Relationship = Relationship
            return cls._Relationship

    @classmethod
    def automap(cls, data, mapRels=True):
        mapped = []

        for item in data:

            if isinstance(item, neo4j.Node):
                mapped.append(cls.Node(item))

            elif isinstance(item, neo4j.Relationship):
                if mapRels:
                    mapped.append(cls.Relationship(item))
                else:
                    mapped.append(item)

            elif isinstance(item, list):
                mapped.append(cls.automap(item, mapRels=mapRels))

            elif isinstance(item, neo4j.Path):
                path = []
                for i, edge in enumerate(item._edges):
                    path.append(cls.Node(item._nodes[i]))
                    if mapRels:
                        path.append(cls.Relationship(edge))
                    else:
                        path.append(edge)
                path.append(cls.Node(item._nodes[-1]))
                mapped.append(path)

            else:
                mapped.append(item)

        return mapped

    def cypher(self, *args, **kwargs):
        automap = kwargs.pop('automap', True)

        results = cypher.execute(self.instance, *args, **kwargs)[0]

        if automap:
            results = self.automap(results, mapRels=False)
            results = self.automap(results, mapRels=True)

        return results

    def batch(self):
        return WriteBatch(self.instance, self.metadata)

class WriteBatch(neo4j.WriteBatch):

    def __init__(self, graph_db, metadata):
        super(WriteBatch, self).__init__(graph_db)
        self.metadata = metadata

    @classproperty
    def Node(cls):
        try:
            return cls._Node
        except AttributeError:
            from node import Node
            cls._Node = Node
            return cls._Node

    @classproperty
    def Relationship(cls):
        try:
            return cls._Relationship
        except AttributeError:
            from relationship import Relationship
            cls._Relationship = Relationship
            return cls._Relationship

    @property
    def phantom_nodes(self):
        try:
            return self._phantom_nodes
        except AttributeError:
            self._phantom_nodes = {}
            return self._phantom_nodes

    @property
    def deleted_nodes(self):
        try:
            return self._deleted_nodes
        except AttributeError:
            self._deleted_nodes = {}
            return self._deleted_nodes

    @property
    def callbacks(self):
        try:
            return self._callbacks
        except AttributeError:
            self._callbacks = []
            return self._callbacks

    def clear(self):
        super(WriteBatch, self).clear()
        self.phantom_nodes.clear()
        self.deleted_nodes.clear()
        self._callbacks = []

    def request_callback(self, func, *args):
        if not hasattr(self.requests[-1], 'callbacks'):
            self.requests[-1].callbacks = []

        if args:
            self.requests[-1].callbacks.append(functools.partial(func, *args))
        else:
            self.requests[-1].callbacks.append(func)

    def batch_callback(self, func, *args):
        if args:
            self.callbacks.append(functools.partial(func, *args))
        else:
            self.callbacks.append(func)

    @property
    def last(self):
        return len(self.requests) - 1

    def create(self, *items):
        for item in items:
            if isinstance(item, self.Node):
                self.create_node(item.get_abstract())
                self.phantom_nodes[item] = self.last

                def callback(item, metadata, response):
                    item._entity = response
                    metadata.session.add(item)

                self.request_callback(callback, item, self.metadata)
                self.create_relationship(self.last, "__instance_of__", item.classnode)

            elif isinstance(item, self.Relationship):
                abstract = [
                    self.phantom_nodes[item.start] if item.start.is_phantom() else item.start._entity,
                    item.type,
                    self.phantom_nodes[item.end] if item.end.is_phantom() else item.end._entity,
                    super(self.Relationship, item).get_abstract()
                ]
                self.create_relationship(*abstract)

                def callback(item, metadata, response):
                    item._entity = response
                    metadata.session.add(item)

                self.request_callback(callback, item, self.metadata)

            elif isinstance(item, dict):
                self.create_node(item)

            elif isinstance(item, Iterable):
                self.create_relationship(*item)

            else:
                raise TypeError(u"cannot create entity from: {0}".format(item))

    def delete(self, *items):
        for item in items:
            if isinstance(item, self.Node):
                def callback(item, response):
                    item.expunge()
                    item._entity = None

                if not item.is_phantom():
                    q = "start n=node({n_id}) "
                    q += "match n-[rels*1]-() foreach(rel in rels: delete rel) "
                    q += "delete n"
                    self.cypher(q, params={'n_id': item.id})
                    self.deleted_nodes[item] = self.last
                    self.request_callback(callback, item)
                else:
                    self.batch_callback(callback, item)

            elif isinstance(item, self.Relationship):
                def callback(item, response):
                    item.expunge()
                    item._entity = None

                if not (item.is_phantom() or \
                        item.start in self.deleted_nodes or \
                        item.end in self.deleted_nodes):
                    self.delete_relationship(item._entity)
                    self.request_callback(callback, item)
                else:
                    self.batch_callback(callback, item)

            elif isinstance(item, neo4j.Node):
                self.delete_node(item)

            elif isinstance(item, neo4j.Relationship):
                self.delete_relationship(item)

            else:
                raise TypeError(u"cannot delete entity from: {0}".format(item))

    def save(self, *entities):
        for entity in entities:
            if isinstance(entity, (self.Node, self.Relationship)):

                if isinstance(entity, self.Node) and entity.is_deleted() or \
                   isinstance(entity, self.Relationship) and (entity.is_deleted() or \
                                                              entity.start.is_deleted() or \
                                                              entity.end.is_deleted()):
                    self.delete(entity)

                elif entity.is_phantom():
                    self.create(entity)

                elif entity.is_dirty():
                    if isinstance(entity, self.Node):
                        self.set_node_properties(entity._entity, entity.get_abstract())
                    else:
                        self.set_relationship_properties(entity._entity, entity.get_abstract())

                    def callback(entity, response):
                        entity.properties.set_dirty(False)

                    self.request_callback(callback, entity)

            else:
                raise TypeError(u"cannot save entity: {0}".format(entity))

    def cypher(self, query, params=None):
        self._post(self._cypher_uri, {"query": query, "params": params or {}})
        self.requests[-1].multirow = True

    def query(self, query):
        self.cypher(query.string, params=query.params)

    def submit(self, automap=True):
        requests = self.requests
        callbacks = self.callbacks
        responses = self._submit()

        results = []
        for response in responses:
            request = requests[response.id]

            if getattr(request, 'multirow', False):
                resolved = [
                    self._graph_db._resolve(item, response.status, id_=response.id)
                    for row in response.body["data"] for item in row
                ]
            else:
                resolved = self._graph_db._resolve(response.body, response.status, id_=response.id)

            if hasattr(request, 'callbacks'):
                for callback in request.callbacks:
                    callback(resolved)

            results.append(resolved)

        if automap:
            results = Engine.automap(results, mapRels=False)
            results = Engine.automap(results, mapRels=True)

        for callback in callbacks:
            callback(results)

        return results
