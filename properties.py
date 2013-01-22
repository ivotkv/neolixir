class PropertyContainer(dict):

    def __init__(self, entity=None):
        super(PropertyContainer, self).__init__()
        self._entity = entity
        self._dirty = False
        self.reload()

    def is_dirty(self):
        return self._dirty

    def set_dirty(self, dirty=True):
        self._dirty = dirty

    def reload(self):
        super(PropertyContainer, self).clear()
        if self._entity:
            for k, v in self._entity.get_properties().iteritems():
                super(PropertyContainer, self).__setitem__(k, v)
        self.set_dirty(False)

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

class Property(object):

    def __init__(self, name=None, nullable=True, default=None):
        self._name = None
        self.name = name
        self.nullable = nullable
        self.default = default

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if self._name is None:
            self._name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        elif self.name is None:
            return None
        else:
            return self._out(instance.properties.get(self.name, self.default))
    
    def __set__(self, instance, value):
        if self.name is not None:
            instance.properties[self.name] = self._in(value)
    
    def __delete__(self, instance):
        if self.name is not None:
            del instance.properties[self.name]

    def _out(self, value):
        return value

    def _in(self, value):
        return value

class Array(Property):
    pass

class Boolean(Property):
    pass

class String(Property):
    pass

class Integer(Property):
    pass

class Float(Property):
    pass

class Decimal(Property):
    pass

class DateTime(Property):
    pass
