from py2neo.neo4j import Node
from py2neo.rest import ResourceNotFound
from neolixir import meta
from entity import Entity, EntityMeta

class NodeEntityMeta(EntityMeta):

    def __init__(cls, name, bases, dict_):
        super(NodeEntityMeta, cls).__init__(name, bases, dict_)

class NodeEntity(Entity):

    __metaclass__ = NodeEntityMeta

    def __init__(self, entity=None, **properties):
        super(NodeEntity, self).__init__(entity, **properties)

    def save(self):
        if self.is_phantom():
            self._entity = meta.engine.create(self.properties)[0]
        elif self.is_dirty():
            self._entity.set_properties(self.properties)
            self.properties.set_dirty(False)

    def delete(self):
        if not self.is_phantom():
            meta.engine.delete(self._entity)

    @classmethod
    def get_by(cls, **kwargs):
        node = None

        if 'id' in kwargs:
            node = meta.engine.get_node(kwargs['id'])

        try:
            return cls(node) if node is not None else None
        except ResourceNotFound:
            return None
