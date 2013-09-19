import threading
from utils import classproperty
from py2neo import neo4j, cypher

class Engine(object):

    def __init__(self, url='http://localhost:7474/db/data/', metadata=None):
        self._threadlocal = threading.local()
        self.metadata = metadata
        self.url = url

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

    @property
    def instance(self):
        try:
            return self._threadlocal.instance
        except AttributeError:
            self._threadlocal.instance = neo4j.GraphDatabaseService(self.url)
            return self._threadlocal.instance

    def automap(self, data, mapRels=True):
        mapped = []

        for item in data:

            if isinstance(item, neo4j.Node):
                mapped.append(self.Node(item))

            elif isinstance(item, neo4j.Relationship):
                if mapRels:
                    mapped.append(self.Relationship(item))
                else:
                    mapped.append(item)

            elif isinstance(item, list):
                mapped.append(self.automap(item, mapRels=mapRels))

            elif isinstance(item, neo4j.Path):
                path = []
                for i, edge in enumerate(item._edges):
                    path.append(self.Node(item._nodes[i]))
                    if mapRels:
                        path.append(self.Relationship(edge))
                    else:
                        path.append(edge)
                path.append(self.Node(item._nodes[-1]))
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

    def _resolve(self, data, status=200, id_=None):
        # NOTE: this is a hacky workaround for arbitrary cypher queries
        # TODO: should not rely on the AssertionError
        try:
            return [item for item in [self._graph_db._resolve(data, status, id_)] if item is not None]
        except AssertionError:
            return [self._graph_db._resolve(item, status, id_) for row in data["data"] for item in row]

    def submit(self):
        # NOTE: copy of original changed to use batch's _resolve
        return [
            self._resolve(response.body, response.status, id_=response.id)
            for response in self._submit()
        ]
