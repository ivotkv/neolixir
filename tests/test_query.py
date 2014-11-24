from common import *
from random import randint

def test_get_by(m):
    v1 = randint(0, 2**30)
    n1 = TNode(integer=v1)
    m.session.commit()
    assert Node.get_by(integer=v1) is n1
    assert TNode.get_by(integer=v1) is n1
    assert SubTNode.get_by(integer=v1) is None
    m.session.clear()
    n1 = Node.get_by(integer=v1)
    assert isinstance(n1, TNode)
    assert n1.integer == v1
    assert TNode.get_by(integer=v1) is n1
    assert SubTNode.get_by(integer=v1) is None
