import threading
from itertools import ifilter
from utils import classproperty
import overrides
from py2neo import neo4j
from py2neo.core import Graph
from py2neo.legacy.core import LegacyResource
from session import Session
from dummy import DummyNode, DummyRelationship
from fast import fast_cypher

__all__ = ['metadata']

class MetaData(object):

    def __init__(self, url='http://localhost:7474/db/data/'):
        self.url = url
        self.session = Session(metadata=self)
        self.classes = {}

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        self._url = url
        self._threadlocal = threading.local()

    @property
    def graph(self):
        try:
            return self._threadlocal.graph
        except AttributeError:
            self._threadlocal.graph = Graph(self.url)
            return self._threadlocal.graph

    @property
    def version(self):
        return self.graph.neo4j_version

    @property
    def legacy(self):
        try:
            return self._threadlocal.legacy
        except AttributeError:
            self._threadlocal.legacy = LegacyResource(self.url)
            return self._threadlocal.legacy

    def add(self, cls):
        self.classes.setdefault(cls.__name__, cls)

    def get(self, name):
        return self.classes.get(name)

    def clear(self):
        self.session = Session(metadata=self)
        self.classes = {}

    def cypher(self, query, params=None, automap=True, fast=False):
        if fast:
            results = fast_cypher(self, query, params=params)
        else:
            results = [list(record) for record in self.graph.cypher.execute(query, params or {})]

        if automap:
            results = self.automap(results, mapRels=False)
            results = self.automap(results, mapRels=True)

        return results

    def batch(self):
        from batch import WriteBatch
        return WriteBatch(self.graph, self)

    @classmethod
    def automap(cls, data, mapRels=True):
        from node import Node
        from relationship import Relationship

        mapped = []

        for item in data:

            if isinstance(item, (DummyNode, neo4j.Node)):
                mapped.append(Node(item))

            elif isinstance(item, (DummyRelationship, neo4j.Relationship)):
                if mapRels:
                    mapped.append(Relationship(item))
                else:
                    mapped.append(item)

            elif isinstance(item, list):
                mapped.append(cls.automap(item, mapRels=mapRels))

            elif isinstance(item, neo4j.Path):
                path = []
                for i, rel in enumerate(item.relationships):
                    path.append(Node(item.nodes[i]))
                    if mapRels:
                        path.append(Relationship(rel))
                    else:
                        path.append(rel)
                path.append(Node(item.nodes[-1]))
                mapped.append(path)

            else:
                mapped.append(item)

        return mapped

    def init(self, reset=False):
        from node import Node

        batch = self.batch()

        if reset:
            for cls in ifilter(lambda x: issubclass(x, Node), self.classes.itervalues()):
                batch.cypher("start c=node({c_id}) match c-[r:__extends__]-() delete r",
                             params={'c_id': cls.classnode.id}, automap=False)

        for cls in ifilter(lambda x: issubclass(x, Node), self.classes.itervalues()):
            c = cls.classnode
            for b in (x.classnode for x in cls.__bases__ if issubclass(x, Node)):
                batch.cypher("start c=node({c_id}), b=node({b_id}) create unique c-[r:__extends__]->b",
                             params={'c_id': c.id, 'b_id': b.id}, automap=False)

        batch.submit()

metadata = MetaData()
