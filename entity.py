from properties import PropertyContainer, Property

class EntityMeta(type):

    def __init__(cls, name, bases, dict_):
        super(EntityMeta, cls).__init__(name, bases, dict_)

        cls._attributes = []
        for k, v in dict_.iteritems():
            if isinstance(v, Property):
                cls._attributes.append(k)
                v.name = k

class Entity(object):
    
    __metaclass__ = EntityMeta

    def __init__(self, entity=None, **properties):
        self._entity = entity
        self._properties = PropertyContainer(self._entity)

        for k, v in properties.iteritems():
            self._properties[k] = v

    def _get_repr_data(self):
        return ["Id = {0}".format(self._entity.id if self._entity else None),
                "Properties = {0}".format(self._properties)]

    def __repr__(self):
        return "<{0} (0x{1:x}): \n{2}\n>".format(self.__class__.__name__, id(self),
                                                 "\n".join(self._get_repr_data()))

    @property
    def properties(self):
        return self._properties

    def is_phantom(self):
        return self._entity is None

    def is_dirty(self):
        return self._properties.is_dirty()

    def reload(self):
        self._properties.reload()
