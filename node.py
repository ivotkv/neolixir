from py2neo.rest import ResourceNotFound
from neolixir import meta
from entity import Entity, EntityMeta

class NodeEntity(Entity):

    def save(self):
        if self.is_phantom():
            self._entity = meta.engine.create(self.properties)[0]
            meta.session.add_entity(self)
            self.properties._entity = self._entity
            self.properties.reload()
        elif self.is_dirty():
            self.properties.save()

    @classmethod
    def get_by(cls, **kwargs):
        node = None

        if 'id' in kwargs:
            node = meta.engine.get_node(kwargs['id'])

        try:
            return cls(node) if node is not None else None
        except ResourceNotFound:
            return None
