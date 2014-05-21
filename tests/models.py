from datetime import datetime
from neolixir import *

class TRel(Relationship):
    pass

class SubTRel(TRel):
    pass

class TNode(Node):
    string = String()

class SubTNode(TNode):
    pass

class IField(Entity):
    ifield = String()

class IFieldTNode(TNode, IField):
    pass
