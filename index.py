from py2neo.neo4j import Node, Relationship
from entity import Entity
from node import NodeEntity
from relationship import RelationshipEntity
from engine import OperationalError
from neolixir import meta

class Index(object):

    _type = Entity
    _defaultkey = '__default_key__'

    def __init__(self, type, name, config=None):
        self._index = meta.engine.get_or_create_index(type, name, config)

    def __getitem__(self, key):
        try:
            return self.get(self._defaultkey, key)[0]
        except IndexError:
            raise KeyError(key)

    def __setitem__(self, key, entity):
        if not self.set(self._defaultkey, key, entity):
            raise OperationalError("failed to set: '{0}'".format(key))

    def __delitem__(self, key):
        self.remove(self._defaultkey, key)

    def add(self, key, value, entity, unique=False):
        func = self._index.add_if_none if unique else self._index.add
        return func(key, value, entity._entity) is not None

    def remove(self, key=None, value=None, entity=None):
        self._index.remove(key, value, entity._entity if entity else None)

    def get(self, key, value=None):
        if value is not None:
            return map(self._type, self._index.get(key, value))
        else:
            return map(self._type, self._index.query("{0}:*".format(key)))

    def set(self, key, value, entity):
        if not self.add(key, value, entity, unique=True):
            # NOTE: will run if the key/value is being set to the same node too
            self.remove(key, value)
            return self.add(key, value, entity, unique=True)
        return True

    def query(self, query):
        return map(self._type, self._index.query(query))

class NodeIndex(Index):

    _type = NodeEntity

    def __init__(self, name, config=None):
        super(NodeIndex, self).__init__(Node, name, config)

class RelationshipIndex(Index):

    _type = RelationshipEntity

    def __init__(self, name, config=None):
        super(RelationshipIndex, self).__init__(Relationship, name, config)
