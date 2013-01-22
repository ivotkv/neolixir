from properties import PropertyContainer

class Entity(object):

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
    def properties():
        return self._properties

    def is_phantom(self):
        return self._entity is None

    def is_dirty(self):
        return self._properties.is_dirty()
