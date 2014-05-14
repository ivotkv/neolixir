from neolixir import *

def test_get(m):
    assert issubclass(m.get('TNode'), Node)
    assert issubclass(m.get('TRel'), Relationship)
