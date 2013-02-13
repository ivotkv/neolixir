import threading
from itertools import ifilter
from py2neo import neo4j
from engine import Engine
from session import Session

__all__ = ['metadata']

class MetaData(object):

    def __init__(self, url='http://localhost:7474/db/data/', debug=False):
        self.url = url
        self.engine = url
        self.debug = debug
        self._session = Session(metadata=self)
        self._classes = {}

    @property
    def engine(self):
        return self._engine.instance

    @engine.setter
    def engine(self, url):
        self._engine = Engine(url=url, metadata=self)

    @property
    def batch(self):
        return self._engine.batch

    @property
    def cypher(self):
        return self._engine.cypher

    @property
    def session(self):
        return self._session

    @property
    def classes(self):
        return self._classes

    def init(self, reset=False):
        from node import Node
        batch = self.batch()
        for cls in ifilter(lambda x: issubclass(x, Node), self.classes.itervalues()):
            n = cls.classnode
            if reset:
                batch.cypher("start n=node({0}) match n-[r:EXTENDS]->() delete r".format(n.id))
            for b in (x.classnode for x in cls.__bases__ if issubclass(x, Node)):
                batch.cypher("start n=node({0}), b=node({1}) create unique n-[r:EXTENDS]->b".format(n.id, b.id))
        batch.submit()

metadata = MetaData()
