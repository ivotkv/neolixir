import threading
from itertools import ifilter
from py2neo import neo4j
from engine import Engine
from session import Session

__all__ = ['metadata']

class MetaData(object):

    def __init__(self, url='http://localhost:7474/db/data/'):
        self.url = url
        self.engine = url
        self._session = Session(metadata=self)
        self._classes = {}

    def add(self, cls):
        self._classes.setdefault(cls.__name__, cls)

    def get(self, name):
        return self._classes.get(name)

    def clear(self):
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
