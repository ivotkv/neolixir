import threading
from utils import classproperty
from py2neo import neo4j
from batch import WriteBatch

class Engine(object):

    __batch_cls__ = WriteBatch

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

    def cypher(self, query, params=None, automap=True):
        query = neo4j.CypherQuery(self.instance, query)
        results = [list(record) for record in query.execute(**params or {})]

        if automap:
            results = self.automap(results, mapRels=False)
            results = self.automap(results, mapRels=True)

        return results

    def batch(self):
        return self.__batch_cls__(self.instance, self.metadata)
