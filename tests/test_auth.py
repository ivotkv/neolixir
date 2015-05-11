from common import *

def test_password_change(m):
    assert m.version >= (2, 2), "Authentication not supported pre-2.2"
    assert m.change_password('neo4j', 'neo4j', 'testpass')
    assert m.change_password('neo4j', 'testpass', 'neo4j')
