from exc import *
from node import Node
from relationship import Relationship
from properties import *
from index import *
from metadata import metadata as m

class SubNode(Node):
    test_id = Integer()
    likes = RelOut('like')
    liked_by = RelIn('like')

class SubSubNode(SubNode):
    name = String()

class SubRel(Relationship):
    pass

class SubSubRel(Relationship):
    pass
