from py2neo.neo4j import Node, Relationship
from metadata import metadata
from exceptions import *
from entity import Entity
from node import NodeEntity
from relationship import RelationshipEntity

class Index(object):

    _type = Entity

    def __init__(self, type, name, config=None):
        self._index = metadata.engine.get_or_create_index(type, name, config)

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

    _type = NodeEntity

    def __init__(self, name, config=None):
        super(NodeIndex, self).__init__(Node, name, config)

class RelationshipIndex(Index):

    _type = RelationshipEntity

    def __init__(self, name, config=None):
        super(RelationshipIndex, self).__init__(Relationship, name, config)
