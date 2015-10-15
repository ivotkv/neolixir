from common import *

def test_node_properties(m):
    n1 = TNode()
    assert n1.is_dirty() == False
    n1.properties['prop1'] = 'prop1'
    assert n1.properties['prop1'] == 'prop1'
    assert n1.is_dirty() == True
    m.session.commit()
    assert n1.is_dirty() == False

    n1.properties['prop1'] = 'prop1'
    assert n1.properties['prop1'] == 'prop1'
    assert n1.is_dirty() == False
    n1.properties['prop1'] = 'prop1-changed'
    assert n1.properties['prop1'] == 'prop1-changed'
    assert n1.is_dirty() == True
    m.session.commit()

    n1_id = n1.id
    n1_entity = n1._entity
    m.session.clear()
    n1 = Node(n1_id)
    assert n1._entity is not n1_entity
    assert n1.is_dirty() == False
    assert n1.properties['prop1'] == 'prop1-changed'

def test_rel_properties(m):
    n1 = TNode()
    n2 = TNode()
    rel = n1.rel_out.append(n2)
    assert rel.is_dirty() == False
    rel.properties['prop1'] = 'prop1'
    assert rel.properties['prop1'] == 'prop1'
    assert rel.is_dirty() == True
    m.session.commit()
    assert rel.is_dirty() == False

    rel.properties['prop1'] = 'prop1'
    assert rel.properties['prop1'] == 'prop1'
    assert rel.is_dirty() == False
    rel.properties['prop1'] = 'prop1-changed'
    assert rel.properties['prop1'] == 'prop1-changed'
    assert rel.is_dirty() == True
    m.session.commit()

    rel_id = rel.id
    rel_entity = rel._entity
    m.session.clear()
    rel = Relationship(rel_id)
    assert rel._entity is not rel_entity
    assert rel.is_dirty() == False
    assert rel.properties['prop1'] == 'prop1-changed'

def test_null(m):
    n1 = TNode()
    n1.properties['prop1'] = 'prop1'
    n1.properties['prop2'] = None
    m.session.commit()

    n1_id = n1.id
    m.session.clear()
    n1 = Node(n1_id)
    assert n1.properties['prop1'] == 'prop1'
    assert 'prop2' not in n1.properties

    n1.properties['prop1'] = None
    m.session.commit()
    m.session.clear()
    n1 = Node(n1_id)
    assert 'prop1' not in n1.properties

def test_string(m):
    n1 = TNode()
    assert n1.is_dirty() == False
    assert n1.string == None
    assert n1.default_string == 'default'

def test_enum(m):
    n1 = TNode()
    assert n1.is_dirty() == False
    assert n1.enum == None
    assert n1.default_enum == 'value1'

    n1.enum = 'value1'
    assert n1.enum == 'value1'
    with raises(ValueError):
        n1.enum = 'invalid'
    assert n1.enum == 'value1'
