from common import *
from py2neo import neo4j

def test_cypher(m):
    n1 = TNode()
    m.session.commit()
    assert isinstance(n1.id, int)

    result = m.cypher("start n=node({n_id}) return n", params={'n_id': n1.id}, automap=False)
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], list)
    assert len(result[0]) == 1
    assert isinstance(result[0][0], neo4j.Node)
    assert result[0][0] == n1._entity

    result = m.cypher("start n=node({n_id}) return n", params={'n_id': n1.id}, automap=True)
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], list)
    assert len(result[0]) == 1
    assert result[0][0] is n1
