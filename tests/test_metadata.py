from common import *

def test_get(m):
    assert m.get('TNode') is TNode
    assert m.get('SubTNode') is SubTNode
    assert m.get('TRel') is TRel
    assert m.get('SubTRel') is SubTRel

def q_classnodes():
    return """
        start n=node({0}),
              tn=node({1}),
              stn=node({2})
    """.format(
        Node.classnode.id,
        TNode.classnode.id,
        SubTNode.classnode.id
    )

def test_init(m):
    q = q_classnodes() + """
        match p=stn-[:__extends__]->tn-[:__extends__]->n return p
    """
    assert len(m.cypher(q, automap=False)) == 1

def test_init_reset(m):
    # create invalid relationship
    q = q_classnodes() + """
        create stn-[r:__extends__]->n return r
    """
    assert len(m.cypher(q, automap=False)) == 1

    # init and re-test
    m.init(reset=True)
    test_init(m)
    
    # check that invalid rel has been deleted
    q = q_classnodes() + """
        match stn-[r:__extends__]->n return r
    """
    assert len(m.cypher(q, automap=False)) == 0
