# -*- coding: utf-8 -*-
# 
# The MIT License (MIT)
# 
# Copyright (c) 2013 Ivaylo Tzvetkov, ChallengeU
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 

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
    
    n1 = TNode()
    res = i.get('key', 'value', n1)
    assert res is n1

    res = i.get('key', 'value', n1)
    assert res is n1

    res = i.get('key', 'value')
    assert len(res) == 1
    assert res[0] is n1

    n1_id = n1.id
    m.session.clear()
    res = i.get('key', 'value')
    assert len(res) == 1
    assert isinstance(res[0], TNode)
    assert res[0].id == n1_id
