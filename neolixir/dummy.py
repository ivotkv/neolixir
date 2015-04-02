import overrides
from py2neo import neo4j

class DummyEntity(object):

    __allowed__ = ['id', 'properties']

    id = None
    properties = None

    def __init__(self, id, properties=None):
        self.id = id
        self.properties = properties or {}

    def __getattribute__(self, name):
        if name.find('__') == 0 or name in object.__getattribute__(self, '__allowed__'):
            return object.__getattribute__(self, name)
        else:
            raise NotImplementedError('attribute not available for {0}: {1}'.format(self.__class__.__name__, name))

    def __repr__(self):
        return u"<{0} (0x{1:x}): ({2}) {3}>".format(self.__class__.__name__, id(self),
                                                    self.id, self.properties)

class DummyNode(DummyEntity, neo4j.Node):

    pass

class DummyRelationship(DummyEntity, neo4j.Relationship):

    __allowed__ = ['id', 'start_node', 'type', 'end_node', 'properties']

    id = None
    start_node = None
    type = None
    end_node = None
    properties = None
    
    def __init__(self, id, start_node, type, end_node, properties=None):
        self.id = id
        self.start_node = start_node
        self.type = type
        self.end_node = end_node
        self.properties = properties or {}

    def __repr__(self):
        return u"<{0} (0x{1:x}): ({2})-[{3}:{4}]->({5}) {6}>".format(self.__class__.__name__, id(self),
                                                                     getattr(self.start_node, 'id', None),
                                                                     self.id, self.type, 
                                                                     getattr(self.end_node, 'id', None),
                                                                     self.properties)
