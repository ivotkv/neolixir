from neolixir import *

def test_get(m):
    assert issubclass(m.get('SubNode'), Node)
    assert issubclass(m.get('SubRel'), Relationship)
