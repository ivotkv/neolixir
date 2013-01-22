from py2neo.neo4j import Node
from py2neo.rest import ResourceNotFound
from neolixir import metadata
from entity import Entity

class NodeEntityMeta(type):

    def __init__(cls, name, bases, dict_):
        cls._instrumented = True if name != 'NodeEntity' else False

class NodeEntity(Entity):
    
    __metaclass__ = NodeEntityMeta

    def __init__(self, entity=None, **properties):
        super(NodeEntity, self).__init__(entity, **properties)

    @classmethod
    def get_by(cls, **kwargs):
        node = None

        if 'id' in kwargs:
            node = metadata.engine.get_node(kwargs['id'])

        try:
            return cls(node) if node is not None else None
        except ResourceNotFound:
            return None
