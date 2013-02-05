import threading
from py2neo import neo4j
from engine import Engine
from session import Session

__all__ = ['metadata']

class MetaData(object):

    def __init__(self, url='http://localhost:7474/db/data/', debug=False):
        self.engine = url
        self.debug = debug
        self._session = Session(metadata=self)
        self._classes = {}
        self._classnodes = threading.local()
        self._classnodes._idmap = {}

    @property
    def engine(self):
        return self._engine.instance

    @engine.setter
    def engine(self, url):
        self._engine = Engine(url=url, metadata=self)

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
            from index import Index
            self._index = Index(neo4j.Node, 'metadata')
            return self._index

    @property
    def classes(self):
        return self._classes

    def classnode(self, cls):
        name = cls.__name__ if isinstance(cls, type) else cls
        try:
            return getattr(self._classnodes, name)
        except AttributeError:
            node = self.index.get('classnode', name, {'__type__': 'classnode', 'classname': name})
            setattr(self._classnodes, name, node)
            self._classnodes._idmap[node.id] = name
            return node

    def class_from_classnode(self, node):
        try:
            name = self._classnodes._idmap[node.id]
        except KeyError:
            name = node.get_properties().get('classname')
            if name is not None:
                self._classnodes._idmap[node.id] = name
        return self._classes.get(name)

    def init(self, reset=False):
        from entity import Entity
        for cls in self.classes.values():
            n = self.classnode(cls)
            if reset:
                self.execute("start n=node({0}) match n-[r:EXTENDS]->() delete r".format(n.id))
            for b in (self.classnode(x) for x in cls.__bases__ if issubclass(x, Entity)):
                self.execute("start n=node({0}), b=node({1}) create unique n-[r:EXTENDS]->b".format(n.id, b.id))

metadata = MetaData()
