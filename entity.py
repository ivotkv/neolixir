from py2neo import neo4j
from util import classproperty
from metadata import metadata as m
from properties import Property, PropertyContainer, FieldDescriptor

__all__ = ['Entity']

class EntityMeta(type):

    def __init__(cls, name, bases, dict_):
        super(EntityMeta, cls).__init__(name, bases, dict_)

        cls._descriptors = cls._descriptors.copy() if hasattr(cls, '_descriptors') else {}
        for k, v in dict_.iteritems():
            if isinstance(v, FieldDescriptor):
                cls._descriptors[k] = v
                v.name = k
        
        m.classes.setdefault(name, cls)

class Entity(object):

    """Base class for all Neolixir entities (Nodes and Relationships).
    
    Defines basic shared functionality and handles proper subclassing and 
    instance initialization, instance registration and descriptor setup.

    Should not be used directly, always use :class:`node.Node` or 
    :class:`relationship.Relationship` instead.

    :param value: A :class:`py2neo.neo4j.Node` or :class:`py2neo.neo4j.Relationship` instance, or None.
    :param \*\*properties: Keyword arguments will be used to initialize the entity's properties.
    :returns: An :class:`Entity` or a subclass thereof.
    
    """
    
    __metaclass__ = EntityMeta

    _initialized = False
    _deleted = False

    def __new__(cls, value=None, **properties):
        if isinstance(value, cls):
            return value
        instance = m.session.get_entity(value)
        if instance is not None:
            return instance
        elif isinstance(value, neo4j.PropertyContainer):
            loaded_properties = value.get_properties()
            valcls = m.classes.get(loaded_properties.get('__class__'))
            if not issubclass(valcls, cls):
                raise TypeError("entity is not an instance of " + cls.__name__)
            instance = super(Entity, cls).__new__(valcls)
            instance._entity = value
            instance._properties = PropertyContainer(instance, loaded_properties)
            if valcls is not cls:
                instance.__init__(value, **properties)
            return instance
        else:
            instance = super(Entity, cls).__new__(cls)
            instance._entity = None
            return instance

    def __init__(self, value=None, **properties):
        if not self._initialized:
            for k, v in properties.iteritems():
                if k in self._descriptors:
                    setattr(self, k, v)
                else:
                    self.properties[k] = v
            self._initialized = True
            m.session.add_entity(self)

    def _get_repr_data(self):
        return ["Id = {0}".format(self.id),
                "Descriptors = {0}".format(sorted(self.descriptors.keys())),
                "Properties = {0}".format(self.properties)]

    def __repr__(self):
        return "<{0} (0x{1:x}): \n{2}\n>".format(self.__class__.__name__, id(self),
                                                 "\n".join(self._get_repr_data()))

    @property
    def id(self):
        return self._entity.id if self._entity else None

    @property
    def descriptors(self):
        return self._descriptors

    @property
    def properties(self):
        try:
            return self._properties
        except AttributeError:
            self._properties = PropertyContainer(self)
            return self._properties

    def get_properties(self):
        data = dict(((k, getattr(self, k)) for k, v in self._descriptors.iteritems() if isinstance(v, Property)))
        for k, v in self.properties.iteritems():
            data.setdefault(k, v)
        return data

    def set_properties(self, data):
        for k, v in data.iteritems():
            if k in self._descriptors:
                setattr(self, k, v)
            else:
                self.properties[k] = v

    def get_abstract(self):
        self.properties.sanitize()
        return self.properties

    def set_entity(self, entity):
        if self._entity is None:
            self._entity = entity
            self.reload()
            return True
        else:
            return False

    def is_phantom(self):
        return self._entity is None

    def is_deleted(self):
        return self._deleted

    def is_dirty(self):
        if self.is_deleted():
            return True
        elif not hasattr(self, '_properties'):
            return False
        else:
            return self.properties.is_dirty()

    def reload(self):
        if hasattr(self, '_properties'):
            self.properties.reload()

    def expunge(self):
        m.session.expunge(self)

    def rollback(self):
        self.reload()

    def delete(self):
        self._deleted = True
        if self.is_phantom():
            self.expunge()

    def undelete(self):
        self._deleted = False
        if self.is_phantom():
            m.session.add_entity(self)

    def save(self):
        raise NotImplementedError("cannot save through generic Entity class")
