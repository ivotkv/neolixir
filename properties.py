class PropertyContainer(dict):

    def __init__(self, entity=None):
        super(PropertyContainer, self).__init__()
        self._entity = entity
        self._dirty = False

        if entity:
            for k, v in entity.get_properties().iteritems():
                self[k] = v

    def is_dirty(self):
        return self._dirty

    def set_dirty(self):
        self._dirty = True

    def __setitem__(self, key, value):
        self.set_dirty()
        super(PropertyContainer, self).__setitem__(key, value)

    def __delitem__(self, key):
        self.set_dirty()
        super(PropertyContainer, self).__delitem__(key)

    def clear(self):
        self.set_dirty()
        super(PropertyContainer, self).clear()

    def pop(self, key, default=None):
        self.set_dirty()
        return super(PropertyContainer, self).pop(key, default)

    def popitem(self):
        self.set_dirty()
        return super(PropertyContainer, self).popitem()

    def setdefault(self, key, default=None):
        self.set_dirty()
        return super(PropertyContainer, self).setdefault(key, default)

    def update(self, *args, **kwargs):
        self.set_dirty()
        return super(PropertyContainer, self).update(*args, **kwargs)

class PropertyDescriptor(object):
    pass
