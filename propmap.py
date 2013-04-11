from py2neo import neo4j
from metadata import metadata as m
from properties import Property

class PropMap(dict):

    def get_properties(self, value):
        if isinstance(value, neo4j.PropertyContainer):
            try:
                return self[value.id]
            except KeyError:
                self[value.id] = PropDict(value.get_properties())
                return self[value.id]
        else:
            try:
                return self[value]
            except KeyError:
                if value.is_phantom():
                    return self.setdefault(value, PropDict())
                else:
                    try:
                        return self[value.id]
                    except:
                        self[value.id] = PropDict(value._entity.get_properties())
                        return self[value.id]

class PropDict(dict):

    def __init__(self, data=None):
        super(PropDict, self).__init__()
        self.owner = None
        if isinstance(data, dict):
            super(PropDict, self).update(data)
        self._dirty = False

    def is_dirty(self):
        return self._dirty

    def set_dirty(self, dirty=True):
        self._dirty = dirty

    def reload(self):
        super(PropDict, self).clear()
        if self.owner and not self.owner.is_phantom():
            super(PropDict, self).update(self.owner._entity.get_properties())
        self.set_dirty(False)

    def sanitize(self):
        super(PropDict, self).__setitem__('__class__', self.owner.__class__.__name__)
        for name, descriptor in self.owner.descriptors.iteritems():
            if isinstance(descriptor, Property) and self.get(name) is None:
                default = descriptor.get_default(self.owner)
                if default is not None:
                    descriptor.__set__(self.owner, default)

    def save(self):
        self.sanitize()
        self.owner._entity.set_properties(self)
        self.set_dirty(False)

    def __setitem__(self, key, value):
        if self.get(key) != value:
            self.set_dirty()
        super(PropDict, self).__setitem__(key, value)

    def __delitem__(self, key):
        self.set_dirty()
        super(PropDict, self).__delitem__(key)

    def clear(self):
        self.set_dirty()
        super(PropDict, self).clear()

    def pop(self, key, default=None):
        self.set_dirty()
        return super(PropDict, self).pop(key, default)

    def popitem(self):
        self.set_dirty()
        return super(PropDict, self).popitem()

    def setdefault(self, key, default=None):
        self.set_dirty()
        return super(PropDict, self).setdefault(key, default)

    def update(self, *args, **kwargs):
        self.set_dirty()
        return super(PropDict, self).update(*args, **kwargs)
