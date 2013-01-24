from metadata import metadata
from properties import PropertyContainer, Property

class EntityMeta(type):

    def __init__(cls, name, bases, dict_):
        super(EntityMeta, cls).__init__(name, bases, dict_)

        attrs = []
        for k, v in dict_.iteritems():
            if isinstance(v, Property):
                attrs.append(k)
                v.name = k
        cls._attributes = tuple(attrs)
        
        metadata.classes[name] = cls

class Entity(object):
    
    __metaclass__ = EntityMeta

    _initialized = False

    def __new__(cls, entity=None, **properties):
        instance = metadata.session.get_entity(entity)
        if instance is not None:
            return instance
        else:
            instance = super(Entity, cls).__new__(cls)
            instance._entity = entity
            metadata.session.add_entity(instance)
            return instance

    def __init__(self, entity=None, **properties):
        if not self._initialized:
            self._properties = PropertyContainer(self._entity)

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

    def rollback(self):
        self.reload()

    def save(self):
        if self.is_phantom():
            raise NotImplementedError("generic Entity cannot create new entities")
        elif self.is_dirty():
            self.properties.save()

    def delete(self):
        if not self.is_phantom():
            metadata.engine.delete(self._entity)
