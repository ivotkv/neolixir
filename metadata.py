import threading
from engine import Engine
from session import Session

class MetaData(object):

    def __init__(self, url='http://localhost:7474/db/data/'):
        self._engine = Engine(url=url, metadata=self)
        self._session = Session(metadata=self)
        self._classes = {}
        self._classnodes = threading.local()

    @property
    def engine(self):
        return self._engine.instance

    @property
    def execute(self):
        return self._engine.execute

    @property
    def session(self):
        return self._session

    @property
    def index(self):
        try:
            return self._index
        except AttributeError:
            from index import NodeIndex
            self._index = NodeIndex('metadata')
            return self._index

    @property
    def classes(self):
        return self._classes

    def classnode(self, cls):
        name = cls.__name__ if isinstance(cls, type) else cls
        try:
            return getattr(self._classnodes, name)
        except AttributeError:
            node = self.index.get('classnode', name, {'type': 'class', 'name': name})
            setattr(self._classnodes, name, node)
            return node

    def init(self, reset=False):
        from entity import Entity
        for cls in self.classes.values():
            n = self.classnode(cls)
            if reset:
                self.execute("START n=node{0} MATCH n-[r:EXTENDS]->() DELETE r".format(n))
            for b in (self.classnode(x) for x in cls.__bases__ if issubclass(x, Entity)):
                self.execute("START n=node{0}, b=node{1} CREATE UNIQUE n-[r:EXTENDS]->b".format(n, b))
