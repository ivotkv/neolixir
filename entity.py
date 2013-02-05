from py2neo import neo4j
from util import classproperty
from metadata import metadata as m
from properties import PropertyContainer, Property, Rel

__all__ = ['Entity']

class EntityMeta(type):

    def __init__(cls, name, bases, dict_):
        super(EntityMeta, cls).__init__(name, bases, dict_)

        cls._descriptors = cls._descriptors.copy() if hasattr(cls, '_descriptors') else set()
        for k, v in dict_.iteritems():
            if isinstance(v, (Property, Rel)):
                cls._descriptors.add(k)
                v.name = k
        
        m.classes[name] = cls

class Entity(object):
    
    __metaclass__ = EntityMeta

    _initialized = False

    def __new__(cls, entity=None, **properties):
        if not isinstance(entity, neo4j.PropertyContainer):
            entity = None
        instance = m.session.get_entity(entity)
        if instance is not None:
            return instance
        else:
            instance = super(Entity, cls).__new__(cls)
            instance._entity = entity
            m.session.add_entity(instance)
            return instance

    def __init__(self, entity=None, **properties):
        if not isinstance(entity, neo4j.PropertyContainer):
            entity = None
        if not self._initialized:
            for k, v in properties.iteritems():
                if k in self._descriptors:
                    setattr(self, k, v)
                else:
                    self.properties[k] = v
            self._initialized = True

    def _get_repr_data(self):
        data = ["Id = {0}".format(self.id),
                "Descriptors = {0}".format(self.descriptors)]
        if m.debug:
            data.append("Properties = {0}".format(self.properties))
        return data

    def __repr__(self):
        return "<{0} (0x{1:x}): \n{2}\n>".format(self.__class__.__name__, id(self),
                                                 "\n".join(self._get_repr_data()))

    def __str__(self):
        return str(self._entity) if self._entity else '()'

    @classproperty
    def classnode(cls):
        return m.classnode(cls)

    @property
    def id(self):
        return self._entity.id if self._entity else None

    @property
    def descriptors(self):
        return self._descriptors

    @property
    def properties(self):
        if getattr(self, '_properties', None) is None:
            self._properties = PropertyContainer(self)
        return self._properties

    def set_entity(self, entity):
        if self._entity is None:
            self._entity = entity
            self.reload()
            return True
        else:
            return False

    def is_phantom(self):
        return self._entity is None

    def is_dirty(self):
        if getattr(self, '_properties', None) is None:
            return False
        else:
            return self.properties.is_dirty()

    def reload(self):
        if getattr(self, '_properties', None) is not None:
            self.properties.reload()

    def expunge(self):
        m.session.expunge(self)

    def rollback(self):
        self.reload()

    def save(self):
        if self.is_phantom():
            raise NotImplementedError("generic Entity cannot create new entities")
        elif self.is_dirty():
            self.properties.save()
        return True

    def delete(self):
        if not self.is_phantom():
            m.engine.delete(self._entity)
