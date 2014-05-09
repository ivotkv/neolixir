from datetime import datetime
from neolixir.entity import Entity
from neolixir.node import Node
from neolixir.relationship import Relationship
from neolixir.properties import *
from neolixir.index import *

class SubRel(Relationship):
    pass

class SubSubRel(SubRel):
    pass

class SubNode(Node):
    test_id = Integer()
    likes = RelOut(SubRel('like'))
    liked_by = RelIn(SubRel('like'))
    knows = RelOut('know')

    one_in = RelInOne(SubRel('one'))
    one_out = RelOutOne(SubRel('one'))

    multiple_in = RelIn('multiple', multiple=True)
    multiple_out = RelOut('multiple', multiple=True)

    date = DateTime(default=datetime.now)

class IField(Entity):
    interface_field = String(default="interface_field_value")

class SubSubNode(SubNode, IField):
    name = String()
    
    enum = Enum('value1', 'value2', 'default', default='default')
