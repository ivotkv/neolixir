from py2neo import neo4j
from util import classproperty
from exc import *
from metadata import metadata as m
from entity import Entity

__all__ = ['Node']

class ClassNode(object):
    
    cache = {}

    @classproperty
    def index(cls):
        try:
            return cls._index
        except AttributeError:
            from index import Index
            cls._index = Index(neo4j.Node, 'ClassNode')
            return cls._index

    @classmethod
    def get(cls, value):
        name = value.__name__ if isinstance(value, type) else value
        try:
            return cls.cache[name]
        except KeyError:
            node = cls.index.get('name', name, {'__class__': 'ClassNode', 'name': name})
            cls.cache[name] = node
            return node

class Node(Entity):

    def __new__(cls, value=None, **properties):
        if isinstance(value, int):
            value = m.engine.get_node(value)
        elif value is not None and not isinstance(value, (cls, neo4j.Node)):
            raise ValueError("Node can only be instantiated by id, entity or None")
        return super(Node, cls).__new__(cls, value, **properties)

    def __init__(self, value=None, **properties):
        if not self._initialized:
            self._relfilters = {}
            super(Node, self).__init__(value, **properties)

    def _get_repr_data(self):
        data = super(Node, self)._get_repr_data()
        if m.debug:
            data.append("Relationships = {0}".format(self.relationships))
        return data

    @classproperty
    def classnode(cls):
        return ClassNode.get(cls)

    @property
    def relationships(self):
        try:
            return self._relfilters['_all']
        except KeyError:
            from relationship import RelationshipFilter
            self._relfilters['_all'] = RelationshipFilter(self)
            if len(self._relfilters) == 1:
                self._relfilters['_all'].reload()
            return self._relfilters['_all']

    def reload(self):
        super(Node, self).reload()
        if len(self._relfilters) > 0:
            self.relationships.reload()

    def delete(self):
        if len(self._relfilters) > 0 or not self.is_phantom():
            for rel in self.relationships:
                rel.delete()
        super(Node, self).delete()

    def undelete(self):
        for rel in self.relationships:
            rel.undelete()
        super(Node, self).undelete()

    def save(self):
        if self.is_deleted():
            if not self.is_phantom():
                q = "start n=node({0}) ".format(self.id)
                q += "match n-[rels*1]->() foreach(rel in rels: delete rel) "
                q += "delete n"
                m.cypher(q)
                self.expunge()
        elif self.is_phantom():
            self._entity = m.engine.create(self.get_abstract(), (0, "INSTANCE_OF", self.classnode))[0]
            m.session.add_entity(self)
        elif self.is_dirty():
            self.properties.save()
        return True

    @classproperty
    def _query(cls):
        return 'start c=node({0}) match c<-[?:EXTENDS|INSTANCE_OF*..]-i where ()<-[:INSTANCE_OF]-i{{0}} return i'.format(cls.classnode.id)

    @classmethod
    def query(cls, **kwargs):
        return cls._query.format("".join((" and i.{0} = {1}".format(k, repr(v)) for k, v in kwargs.iteritems())))

    @classmethod
    def get_by(cls, **kwargs):
        results = []
        if 'id' in kwargs:
            results.append(cls(kwargs['id']))
        else:
            for node in m.cypher(cls.query(**kwargs)):
                results.append(cls(node))
        return results
