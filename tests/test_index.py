from common import *

def test_node_index(m):
    i = NodeIndex('TestNodeIndex')
    i.clear()

    res = i.get('key', 'value')
    assert isinstance(res, list)
    assert len(res) == 0

    res = i.get('key', 'value', TNode())
    assert isinstance(res, TNode)

    res = i.get('key', 'value')
    assert len(res) == 1
    assert isinstance(res[0], TNode)

    i.clear()
    res = i.get('key', 'value')
    assert len(res) == 0
