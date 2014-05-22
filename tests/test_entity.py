from common import *

def test_interface_inheritance(m):
    assert hasattr(IFieldTNode, 'ifield')
    assert 'ifield' in IFieldTNode._descriptors
    assert IFieldTNode.ifield.name == 'ifield'

    n1 = IFieldTNode()
    assert hasattr(n1, 'ifield')
    assert 'ifield' in n1._descriptors
    assert n1.ifield is None

    n1.ifield = 'ifield'
    assert n1.ifield == 'ifield'
    assert n1.properties['ifield'] == 'ifield'

    m.session.commit()
    n1_id = n1.id
    m.session.clear()
    n1 = Node(n1_id)
    assert isinstance(n1, IFieldTNode)
    assert hasattr(n1, 'ifield')
    assert 'ifield' in n1._descriptors
    assert n1.ifield == 'ifield'
    assert n1.properties['ifield'] == 'ifield'
