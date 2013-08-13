from py2neo import neo4j
from metadata import metadata as m
from exc import *
from entity import Entity
from node import Node
from relationship import Relationship

__all__ = ['NodeIndex', 'RelationshipIndex']

class Index(object):

    def __init__(self, type, name, config=None):
        self.type = type
        self.name = name
        self.config = config

    @property
    def index(self):
        try:
            return self._index
        except AttributeError:
            self._index = m.engine.get_or_create_index(self.type, self.name, self.config)
            return self._index

    def clear(self):
        m.engine.delete_index(self.type, self.name)
        try:
            delattr(self, '_index')
        except AttributeError:
            pass

    def add(self, key, value, entity, if_none=False):
        if isinstance(entity, Entity):
            entity = entity._entity
        func = self.index.add_if_none if if_none else self.index.add
        return func(str(key), str(value), entity) is not None

    def get(self, key, value=None, abstract=None):
        if value is None:
            return self.index.query("{0}:*".format(key))
        elif abstract is None:
            return self.index.get(str(key), str(value))
        else:
            return self.index.get_or_create(str(key), str(value), abstract)

    def query(self, query):
        return self.index.query(query)

    def remove(self, key=None, value=None, entity=None):
        if isinstance(entity, Entity):
            entity = entity._entity
        self.index.remove(str(key), str(value), entity)

class NodeIndex(Index):

    def __init__(self, name, config=None, cls=None):
        super(NodeIndex, self).__init__(neo4j.Node, name, config)
        self.cls = cls

    def get(self, key, value=None, item=None):
        if isinstance(item, dict):
            if self.cls:
                node = self.cls(value=None, **item)
            else:
                node = Node(value=None, **item)
            return self.get(key, value, node)
        elif isinstance(item, Node):
            if item.is_phantom():
                n = super(NodeIndex, self).get(key, value, item.get_abstract())
                c = item.classnode
                if len(m.cypher('start n=node({n_id}), c=node({c_id}) where not n-[:__instance_of__]->() create unique n-[r:__instance_of__]->c return r', params={'n_id': n.id, 'c_id': c.id}, automap=False)) > 0:
                    item.set_entity(n)
                    return item
                else:
                    item.expunge()
                    return Node(n)
            else:
                if self.add(key, value, item, if_none=True):
                    return item
                else:
                    return Node(super(NodeIndex, self).get(key, value)[0])
        else:
            return map(Node, super(NodeIndex, self).get(key, value))

    def query(self, query):
        return map(Node, super(NodeIndex, self).query(query))

class RelationshipIndex(Index):

    def __init__(self, name, config=None):
        super(RelationshipIndex, self).__init__(neo4j.Relationship, name, config)
