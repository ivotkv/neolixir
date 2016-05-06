from common import *
from random import randint

def test_elixir_compat(m):
    v1 = randint(0, 2**30)
    q = TNode.query.append('where instance.integer = {0} return instance'.format(v1))
    assert q.count() == 0
    assert q.first() is None
    with raises(QueryError):
        q.one()
    n1 = TNode(integer=v1)
    m.session.commit()
    assert q.count() == 1
    assert q.first() is n1
    assert q.one() is n1
    n2 = TNode(integer=v1)
    m.session.commit()
    assert q.count() == 2
    assert q.first() in (n1, n2)
    with raises(QueryError):
        q.one()

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
