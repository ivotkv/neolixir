from datetime import datetime as datetime_
from decimal import Decimal
from neolixir import *

class TRel(Relationship):
    string = String()

class SubTRel(TRel):
    substring = String()

class TNode(Node):
    boolean = Boolean()
    string = String()
    enum = Enum('value1', 'value2')
    integer = Integer()
    float = Float()
    numeric = Numeric()
    datetime = DateTime()

    default_boolean = Boolean(default=True)
    default_string = String(default='default')
    default_enum = Enum('value1', 'value2', default='value1')
    default_integer = Integer(default=1)
    default_float = Float(default=1.0)
    default_numeric = Numeric(default=Decimal('1.00'))
    default_datetime = DateTime(default=datetime_(2010, 10, 10))

    rel_out = RelOut('rel_out')
    rel_in = RelIn('rel_in')

    rel_out_one = RelOutOne('rel_out_one')
    rel_in_one = RelInOne('rel_in_one')

    rel_out_multiple = RelOutOne('rel_out_multiple', multiple=True)
    rel_in_multiple = RelInOne('rel_in_multiple', multiple=True)

class SubTNode(TNode):
    substring = String()

class IField(Entity):
    ifield = String()

class IFieldTNode(TNode, IField):
    pass
