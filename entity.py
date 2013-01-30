from util import classproperty
from metadata import metadata as m
from properties import PropertyContainer, Property, Rel

__all__ = ['Entity']

class EntityMeta(type):

    def __init__(cls, name, bases, dict_):
        super(EntityMeta, cls).__init__(name, bases, dict_)

        if not hasattr(cls, '_attributes'):
            cls._attributes = set()
        for k, v in dict_.iteritems():
            if isinstance(v, (Property, Rel)):
                cls._attributes.add(k)
                v.name = k
        
        m.classes[name] = cls

class Entity(object):
    
    __metaclass__ = EntityMeta

    _initialized = False

    def __new__(cls, entity=None, **properties):
        instance = m.session.get_entity(entity)
        if instance is not None:
            return instance
        else:
            instance = super(Entity, cls).__new__(cls)
            instance._entity = entity
            m.session.add_entity(instance)
            return instance

    def __init__(self, entity=None, **properties):
        if not self._initialized:
            self._properties = PropertyContainer(self)

            for k, v in properties.iteritems():
                if k in self._attributes:
                    setattr(self, k, v)
                else:
                    self._properties[k] = v

            self._initialized = True

    def _get_repr_data(self):
        return ["Id = {0}".format(self.id),
                "Attributes = {0}".format(self.attributes),
                "Properties = {0}".format(self.properties)]

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
    def attributes(self):
        return self._attributes

    @property
    def properties(self):
        return self._properties

    def is_phantom(self):
        return self._entity is None

    def is_dirty(self):
        return self.properties.is_dirty()

    def reload(self):
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
