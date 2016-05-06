from common import *
from random import randint

def test_tokenize(m):
    from neolixir.query import tokenize

def test_append(m):
    q = TNode.query
    assert q.string == 'match (instance:TNode) return instance'

def test_elixir_compat(m):
    q = TNode.query
    assert q.string == 'match (instance:TNode) return instance'
    q = q.offset(0)
    assert q.string == 'match (instance:TNode) return instance skip 0'
    q = q.limit(10)
    assert q.string == 'match (instance:TNode) return instance skip 0 limit 10'
    q = q.offset(10)
    assert q.string == 'match (instance:TNode) return instance skip 10'
    q = q.limit(20)
    assert q.string == 'match (instance:TNode) return instance skip 10 limit 20'
    q = q.limit(30)
    assert q.string == 'match (instance:TNode) return instance skip 10 limit 30'
    q = q.append('return count(*)')
    assert q.string == 'match (instance:TNode) return count(*)'

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
