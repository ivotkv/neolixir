from exc import *
from node import Node
from relationship import Relationship
from properties import *
from metadata import metadata as m

class SubNode(Node):
    test_id = Integer()

class SubSubNode(SubNode):
    pass

class SubRel(Relationship):
    pass

class SubSubRel(Relationship):
    pass
