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

def test_plain(m):
    n1 = TNode()
    n2 = TNode()
    assert len(n1.rel_out) == 0
    assert len(n1.rel_in) == 0
    r = Relationship.get((n1, 'rel', n2))
    assert r in n1.rel_out
    assert n2 in n1.rel_out
    assert r in n2.rel_in
    assert n1 in n2.rel_in
    r.delete()
    n1.rel_in.append(n2)
    assert n2 in n1.rel_in
    assert n1 in n2.rel_out
    n2.rel_out.remove(n1)
    assert n2 not in n1.rel_in
    assert n1 not in n2.rel_out

    # relview
    assert n1.rel_out is n1.relview('rel_out')
    assert n1.rel_in is n1.relview('rel_in')
    assert n1.relview('rel_out') is not n1.relview('rel_in')
    assert n2.rel_out is n2.relview('rel_out')
    assert n1.relview('rel_out') is not n2.relview('rel_out')

    # no multiples by default
    assert len(n1.rel_out) == 0
    assert len(n2.rel_in) == 0
    n1.rel_out.append(n2)
    assert len(n1.rel_out) == 1
    assert len(n2.rel_in) == 1
    n1.rel_out.append(n2)
    n2.rel_in.append(n1)
    assert len(n1.rel_out) == 1
    assert len(n2.rel_in) == 1
    n1.rel_out.remove(n2)
    assert len(n1.rel_out) == 0
    assert len(n2.rel_in) == 0

    # self-reference
    n1.rel_out.append(n1)
    assert n1 in n1.rel_out
    assert n1 in n1.rel_in
    n1.rel_out.remove(n1)
    assert n1 not in n1.rel_out
    assert n1 not in n1.rel_in

def test_subclass(m):
    pass

def test_one(m):
    n1 = TNode()
    n2 = TNode()
    assert n1.rel_in_one is None
    assert n2.rel_out_one is None
    n1.rel_in_one = n2
    assert n1.rel_in_one is n2
    assert n2.rel_out_one is n1
    assert n1.relview('rel_in_one').rel() is n2.relview('rel_out_one').rel()
    n1.rel_in_one = None
    assert n1.rel_in_one is None
    assert n2.rel_out_one is None
    n1.rel_in_one = n2
    n2.rel_out_one = None
    assert n1.rel_in_one is None
    assert n2.rel_out_one is None
    n1.rel_in_one = n1
    assert n1.rel_in_one is n1
    assert n1.rel_out_one is n1
    n1.rel_in_one = None
    assert n1.rel_in_one is None
    assert n1.rel_out_one is None

    # relview
    n1.rel_in_one = None
    assert n1.relview('rel_in_one') is not n1.rel_in_one
    assert len(n1.relview('rel_in_one')) == 0
    n1.rel_in_one = n2
    assert n1.relview('rel_in_one') is not n1.rel_in_one
    assert len(n1.relview('rel_in_one')) == 1
    assert n1.relview('rel_in_one')[0] is n2

def test_multiple(m):
    n1 = TNode()
    n2 = TNode()
    assert len(n1.rel_in_multiple) is 0
    assert len(n2.rel_out_multiple) is 0
    n1.rel_in_multiple.append(n2)
    assert len(n1.rel_in_multiple) is 1
    assert len(n2.rel_out_multiple) is 1
    n1.rel_in_multiple.append(n2)
    assert len(n1.rel_in_multiple) is 2
    assert len(n2.rel_out_multiple) is 2
    assert len(set(n1.rel_in_multiple)) is 1
    assert len(set(n2.rel_out_multiple)) is 1
    assert list(set(n1.rel_in_multiple))[0] is n2
    assert list(set(n2.rel_out_multiple))[0] is n1
    n1.rel_in_multiple.remove(n1.rel_in_multiple.rel(n2)[0])
    assert len(n1.rel_in_multiple) is 1
    assert len(n2.rel_out_multiple) is 1
    n1.rel_in_multiple.append(n2)
    n2.rel_out_multiple.append(n1)
    assert len(n1.rel_in_multiple) is 3
    assert len(n2.rel_out_multiple) is 3
    assert n2 in n1.rel_in_multiple
    assert n2 not in n1.rel_out_multiple
    assert n1 in n2.rel_out_multiple
    assert n1 not in n2.rel_in_multiple
