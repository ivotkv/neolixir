from py2neo import neo4j
from util import classproperty
from exceptions import *
from metadata import metadata as m
from entity import Entity

__all__ = ['Node']

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

    def save(self):
        if self.is_phantom():
            classnode = self.classnode
            self.set_entity(m.engine.create(self.properties, (0, "INSTANCE_OF", classnode))[0])
            m.session.add_entity(self)
        elif self.is_dirty():
            self.properties.save()
        return True

    @classproperty
    def _query(cls):
        return 'start n=node({0}) match p=n<-[?:EXTENDS|INSTANCE_OF*..]-i where ()<-[:INSTANCE_OF]-i{{0}} return i, p'.format(cls.classnode.id)

    @classmethod
    def query(cls, **kwargs):
        return cls._query.format("".join((" and i.{0} = {1}".format(k, repr(v)) for k, v in kwargs.iteritems())))

    @classmethod
    def get(cls, value, classname=None):
        if isinstance(value, cls):
            return value
        elif isinstance(value, int):
            value = m.engine.get_node(value)
        elif not isinstance(value, neo4j.Node):
            return None

        if classname is None:
            classname = cls.get_classname_from_id(value.id)

        nodeclass = m.classes.get(classname)
        if nodeclass is None or not issubclass(nodeclass, cls):
            return None

        try:
            return nodeclass(value)
        except ResourceNotFound:
            return None

    @classmethod
    def get_by(cls, **kwargs):
        if 'id' in kwargs:
            try:
                n, c = m.cypher('start n=node({0}) match n-[?:INSTANCE_OF]->c return n, c.classname'.format(kwargs['id']))[0]
                return cls.get(n, c)
            except (CypherError, IndexError):
                return None
        else:
            results = []
            for node, path in m.cypher(cls.query(**kwargs)):
                c = m.class_from_classnode(path.nodes[-2])
                if c is not None:
                    results.append(c(node))
            return results
        return None

    @classmethod
    def get_classname_from_id(cls, id):
        if m.session.nodes.has_key(id):
            return m.session.nodes[id].__class__.__name__
        try:
            return m.cypher('start n=node({0}) match n-[?:INSTANCE_OF]->c return c.classname'.format(id))[0][0]
        except (CypherError, IndexError):
            return None
