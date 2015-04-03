class DummyEntity(object):

    __slots__ = ['id', 'properties']

    def __init__(self, id, properties=None):
        self.id = id
        self.properties = properties or {}

    def __repr__(self):
        return "<{0} (0x{1:x}): ({2}) {3}>".format(self.__class__.__name__, id(self),
                                                   self.id, self.properties)

class DummyNode(DummyEntity):

    __slots__ = []

class DummyRelationship(DummyEntity):

    __slots__ = ['start_node', 'type', 'end_node']
    
    def __init__(self, id, start_node, type, end_node, properties=None):
        self.id = id
        self.start_node = start_node
        self.type = type
        self.end_node = end_node
        self.properties = properties or {}

    def __repr__(self):
        return "<{0} (0x{1:x}): ({2})-[{3}:{4}]->({5}) {6}>".format(self.__class__.__name__, id(self),
                                                                    getattr(self.start_node, 'id', None),
                                                                    self.id, self.type, 
                                                                    getattr(self.end_node, 'id', None),
                                                                    self.properties)
