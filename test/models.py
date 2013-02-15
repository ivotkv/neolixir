from datetime import datetime
from exc import *
from node import Node
from relationship import Relationship
from properties import *
from index import *
from metadata import metadata as m

class SubRel(Relationship):
    pass

class SubSubRel(Relationship):
    pass

class SubNode(Node):
    test_id = Integer()
    likes = RelOut(SubRel('like'))
    liked_by = RelIn('like', SubRel)
    knows = RelOut('know')
    date = DateTime(default=datetime.now)

class SubSubNode(SubNode):
    name = String()
