from util import classproperty
from exceptions import *
from metadata import metadata as m
from entity import Entity

__all__ = ['Node']

class Node(Entity):

    def save(self):
        if self.is_phantom():
            classnode = m.classnode(self.__class__)
            self._entity = m.engine.create(self.properties, (0, "INSTANCE_OF", classnode._entity))[0]
            m.session.add_entity(self)
            self.properties._entity = self._entity
            self.properties.reload()
        elif self.is_dirty():
            self.properties.save()

    @classmethod
    def from_node(cls, node, classname=None):
        if classname is not None:
            nodeclass = m.classes.get(classname, cls)
            if issubclass(nodeclass, cls):
                cls = nodeclass
            else:
                return None
        return cls(node) if node is not None else None

    @classproperty
    def _query(cls):
        return 'start n=node({0}) match p=n<-[?:EXTENDS|INSTANCE_OF*..]-i where ()<-[:INSTANCE_OF]-i{{0}} return i, p'.format(cls.classnode.id)

    @classmethod
    def query(cls, **kwargs):
        return cls._query.format("".join((" and i.{0} = {1}".format(k, repr(v)) for k, v in kwargs.iteritems())))

    @classmethod
    def get_by(cls, **kwargs):
        if 'id' in kwargs:
            try:
                n, c = m.execute('start n=node({0}) match n-[?:INSTANCE_OF]->c return n, c.classname'.format(kwargs['id']))[0]
                return cls.from_node(n, c)
            except (CypherError, IndexError):
                return None
        else:
            results = []
            for node, path in m.execute(cls.query(**kwargs)):
                c = m.class_from_classnode(path.nodes[-2])
                if c is not None:
                    results.append(c(node))
            return results
        return None
