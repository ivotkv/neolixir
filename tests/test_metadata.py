# -*- coding: utf-8 -*-
# 
# The MIT License (MIT)
# 
# Copyright (c) 2013 Ivo Tzvetkov
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 

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

def test_automap(m):
    n1 = TNode()
    n2 = TNode()
    rel = n1.rel_out.append(n2)
    trel = n1.trel_out.append(n2)
    m.session.commit()
    assert isinstance(n1.id, int)
    assert isinstance(n2.id, int)
    assert isinstance(rel.id, int)
    assert isinstance(trel.id, int)

    result = m.cypher("""
        start n1=node({n1_id}), n2=node({n2_id})
        match n1-[rel:rel]->n2,
              n1-[trel:trel]->n2
        return n1, n2, rel, trel
    """, params = {
        'n1_id': n1.id,
        'n2_id': n2.id
    }, automap=True)
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], list)
    assert len(result[0]) == 4
    assert result[0][0] is n1
    assert result[0][1] is n2
    assert result[0][2] is rel
    assert result[0][3] is trel

    result = m.cypher("""
        start n1=node({n1_id})
        match n1-[rel:rel|trel]->n2
        return n1, collect(distinct n2), collect(distinct rel)
    """, params = {
        'n1_id': n1.id
    }, automap=True)
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], list)
    assert len(result[0]) == 3
    assert result[0][0] is n1
    assert isinstance(result[0][1], list)
    assert len(result[0][1]) == 1
    assert result[0][1][0] is n2
    assert isinstance(result[0][2], list)
    assert len(result[0][2]) == 2
    assert rel in result[0][2]
    assert trel in result[0][2]

    result = m.cypher("""
        start n1=node({n1_id})
        match p=n1-[:rel]->()<-[:trel]-()
        return p
    """, params = {
        'n1_id': n1.id
    }, automap=True)
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], list)
    assert len(result[0]) == 1
    assert isinstance(result[0][0], list)
    assert len(result[0][0]) == 5
    assert result[0][0][0] is n1
    assert result[0][0][1] is rel
    assert result[0][0][2] is n2
    assert result[0][0][3] is trel
    assert result[0][0][4] is n1

    result = m.cypher("""
        start n1=node({n1_id})
        match p=n1-[:rel|trel]->()
        return n1, collect(p)
    """, params = {
        'n1_id': n1.id
    }, automap=True)
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], list)
    assert len(result[0]) == 2
    assert result[0][0] is n1
    assert isinstance(result[0][1], list)
    assert len(result[0][1]) == 2
    for i in range(2):
        assert isinstance(result[0][1][i], list)
        assert len(result[0][1][i]) == 3
        assert result[0][1][i][0] is n1
        assert result[0][1][i][1] is rel or result[0][1][i][1] is trel
        assert result[0][1][i][2] is n2

def test_get(m):
    assert m.get('TNode') is TNode
    assert m.get('SubTNode') is SubTNode
    assert m.get('TRel') is TRel
    assert m.get('SubTRel') is SubTRel
