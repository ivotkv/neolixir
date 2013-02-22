"""Contains various general utilities."""

class classproperty(object):
    """
    A decorator allowing the definition of class properties, e.g.::

        @classproperty
        def classname(cls):
            return cls.__name__

    """

    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)
