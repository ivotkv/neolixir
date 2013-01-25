from exceptions import *
from metadata import metadata as m
from entity import Entity

__all__ = ['Node']

class Node(Entity):

    def save(self):
        if self.is_phantom():
            classnode = m.classnode(self.__class__)
            self._entity = m.engine.create(self.properties, (0, "INSTANCE_OF", classnode))[0]
            m.session.add_entity(self)
            self.properties._entity = self._entity
            self.properties.reload()
        elif self.is_dirty():
            self.properties.save()

    @classmethod
    def get_by(cls, **kwargs):
        if 'id' in kwargs:
            try:
                n, c = m.execute('start n=node({0}) match n-[?:INSTANCE_OF]->c return n, c'.format(kwargs['id']))
                if c is not None:
                    c = m.classes.get(c, cls)
                    if issubclass(c, cls):
                        cls = c
                    else:
                        return None
                return cls(n) if n is not None else None
            except CypherError:
                return None
        return None
