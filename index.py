from py2neo import neo4j
from metadata import metadata as m
from exceptions import *
from entity import Entity
from node import Node
from relationship import Relationship

__all__ = ['NodeIndex', 'RelationshipIndex']

class Index(object):

    def __init__(self, type, name, config=None):
        self._index = m.engine.get_or_create_index(type, name, config)

    @property
    def name(self):
        return self._index.name

    def add(self, key, value, entity, if_none=False):
        if isinstance(entity, Entity):
            entity = entity._entity
        func = self._index.add_if_none if if_none else self._index.add
        return func(str(key), str(value), entity) is not None

    def get(self, key, value=None, abstract=None):
        if value is None:
            return self._index.query("{0}:*".format(key))
        elif abstract is None:
            return self._index.get(str(key), str(value))
        else:
            return self._index.get_or_create(str(key), str(value), abstract)

    def query(self, query):
        return self._index.query(query)

    def remove(self, key=None, value=None, entity=None):
        if isinstance(entity, Entity):
            entity = entity._entity
        self._index.remove(str(key), str(value), entity)

class NodeIndex(Index):

    def __init__(self, name, config=None):
        super(NodeIndex, self).__init__(neo4j.Node, name, config)

    def get(self, key, value=None, item=None):
        if isinstance(item, dict):
            return Node(super(NodeIndex, self).get(key, value, item))
        elif isinstance(item, Node):
            if item.is_phantom():
                n = super(NodeIndex, self).get(key, value, item.properties)
                c = item.classnode
                if len(m.cypher('start n=node({0}), c=node({1}) where not n-[:INSTANCE_OF]->() create unique n-[r:INSTANCE_OF]->c return r'.format(n.id, c.id))) > 0:
                    item.set_entity(n)
                    return item
                else:
                    return Node.get(n)
            else:
                if self.add(key, value, item, if_none=True):
                    return item
                else:
                    return Node.get(super(NodeIndex, self).get(key, value)[0])
        else:
            return map(Node.get, super(NodeIndex, self).get(key, value))

    def query(self, query):
        return map(Node.get, super(NodeIndex, self).query(query))

class RelationshipIndex(Index):

    def __init__(self, name, config=None):
        super(RelationshipIndex, self).__init__(neo4j.Relationship, name, config)
