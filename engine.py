import threading
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
            from node import Relationship
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
        return WriteBatch(self.instance)

class WriteBatch(neo4j.WriteBatch):

    def cypher(self, query, params=None):
        self._post(self._cypher_uri, {"query": query, "params": params or {}})
        self.requests[-1].multirow = True

    def query(self, query):
        self.cypher(query.string, params=query.params)

    def submit(self, automap=True):
        requests = self.requests
        responses = self._submit()

        results = []
        for response in responses:
            if getattr(requests[response.id], 'multirow', False):
                results.append([
                    self._graph_db._resolve(item, response.status, id_=response.id)
                    for row in response.body["data"] for item in row
                ])
            else:
                results.append(self._graph_db._resolve(response.body, response.status, id_=response.id))

        if automap:
            results = Engine.automap(results, mapRels=False)
            results = Engine.automap(results, mapRels=True)

        return results
