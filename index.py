from py2neo import neo4j
from metadata import metadata as m
from exceptions import *
from entity import Entity
from node import Node
from relationship import Relationship

class Index(object):

    _type = Entity

    def __init__(self, type, name, config=None):
        self._index = m.engine.get_or_create_index(type, name, config)

    @property
    def name(self):
        return self._index.name

    def add(self, key, value, entity, if_none=False):
        func = self._index.add_if_none if if_none else self._index.add
        return func(key, value, entity._entity) is not None

    def get(self, key, value=None, abstract=None):
        if value is None:
            return map(self._type, self._index.query("{0}:*".format(key)))
        elif abstract is None:
            return map(self._type, self._index.get(key, value))
        else:
            return self._type(self._index.get_or_create(key, value, abstract))

    def query(self, query):
        return map(self._type, self._index.query(query))

    def remove(self, key=None, value=None, entity=None):
        self._index.remove(key, value, entity._entity if entity else None)

class NodeIndex(Index):

    _type = Node

    def __init__(self, name, config=None):
        super(NodeIndex, self).__init__(neo4j.Node, name, config)

class RelationshipIndex(Index):

    _type = Relationship

    def __init__(self, name, config=None):
        super(RelationshipIndex, self).__init__(neo4j.Relationship, name, config)
