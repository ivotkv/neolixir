from datetime import datetime
from exc import *
from entity import Entity
from node import Node
from relationship import Relationship
from properties import *
from index import *
from metadata import metadata as m

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
