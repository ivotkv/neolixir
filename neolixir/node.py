import overrides
from py2neo import neo4j
from utils import classproperty
from exc import *
from metadata import metadata as m
from entity import Entity
from query import Query

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
    
    __query_cls__ = Query

    def __new__(cls, value=None, **properties):
        if isinstance(value, int):
            try:
                value = m.graph.node(value)
            except ValueError as e:
                if str(e).find('not found') > 0:
                    raise EntityNotFoundException(str(e))
                raise e
        elif value is not None and not isinstance(value, (cls, neo4j.Node)):
            raise ValueError("Node can only be instantiated by id, entity or None")
        return super(Node, cls).__new__(cls, value, **properties)

    def __init__(self, value=None, **properties):
        self._relfilters = {}
        super(Node, self).__init__(value, **properties)

    @classproperty
    def classnode(cls):
        return ClassNode.get(cls)

    def relview(self, name):
        descriptor = getattr(self.__class__, name)
        return descriptor.get_relview(self)

    def delete(self):
        try:
            while True:
                m.session.relmap.node[self].pop().delete()
        except KeyError:
            pass
        super(Node, self).delete()

    def save(self, batch=None):
        if batch:
            batch.save(self)

        else:
            if self.is_deleted():
                if not self.is_phantom():
                    q = "start n=node({n_id}) "
                    q += "match n-[rels*1]-() foreach(rel in rels: delete rel) "
                    q += "delete n"
                    m.cypher(q, params={'n_id': self.id})
                self.expunge()
                self._entity = None

            elif self.is_phantom():
                self._entity = m.graph.create(self.get_abstract(), (0, "__instance_of__", self.classnode))[0]
                m.session.add(self)

            elif self.is_dirty():
                self.properties.save()

        return True

    @classproperty
    def query(cls):
        return cls.__query_cls__.node(cls)

    @classmethod
    def get_by(cls, **kwargs):
        if 'id' in kwargs:
            try:
                return cls(kwargs['id'])
            except EntityNotFoundException:
                return None
        else:
            return cls.query.filter(*["instance.{0}! = {1}".format(k, repr(v)) for k, v in kwargs.iteritems()]).first()
