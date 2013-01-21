from py2neo.neo4j import Node
from engine import get_engine

class NodeEntityMeta(type):

    def __new__(cls, name, bases, dict_):
        attrs = ((name, value) for name, value in dct.items() if not name.startswith('__'))
        uppercase_attr = dict((name.upper(), value) for name, value in attrs)

        return super(NodeEntityMeta, cls).__new__(cls, name, bases, dict_)

class NodeEntity(Node):

    __metaclass__ = NodeEntityMeta

    def __init__(self, **kwargs):
        pass

    @classmethod
    def get_by(cls, **kwargs):
        e = get_engine()
        if 'id' in kwargs:
            return e.get_node(kwargs['id'])
        else:

