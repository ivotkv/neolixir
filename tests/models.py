from datetime import datetime
from neolixir import *

class TRel(Relationship):
    string = String()

class SubTRel(TRel):
    substring = String()

class TNode(Node):
    boolean = Boolean()
    string = String()
    enum = Enum()
    integer = Integer()
    float = Float()
    numeric = Numeric()
    datetime = DateTime()

    default = String(default='default')

    rel_out = RelOut('rel_out')
    rel_in = RelIn('rel_in')

    rel_out_one = RelOutOne('rel_out_one')
    rel_in_one = RelInOne('rel_in_one')

class SubTNode(TNode):
    substring = String()

class IField(Entity):
    ifield = String()

class IFieldTNode(TNode, IField):
    pass
