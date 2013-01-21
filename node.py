class NodeMeta(type):
    pass

class NodeBase(object):

    @classmethod
    def query(cls, *args, **kwargs):
        return None

    @classmethod
    def get_by(cls, *args, **kwargs):
        return None

class Node(NodeBase):
    __metaclass__ = NodeMeta
