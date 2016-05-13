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
from random import randint

def test_tokenize(m):
    from neolixir.query import tokenize
    string = """
    """
    assert tokenize(string) == [
    ]
    string = """
        start user=node({user_id}), location=node({location_id})
        match (location)<-[:lives_in|lives_near]-neighbour
        with collect(user) + collect(neighbour) as people
        unwind people as person
        with distinct person
        match person-[:knows*1..4]->(other {name: "Bob"})
        return count(*)
    """
    assert tokenize(string) == [
        'start', 'user=node({user_id}),', 'location=node({location_id})',
        'match', '(location)<-[:lives_in|lives_near]-neighbour',
        'with', 'collect(user)', '+', 'collect(neighbour)', 'as', 'people',
        'unwind', 'people', 'as', 'person',
        'with', 'distinct', 'person',
        'match', 'person-[:knows*1..4]->(other {name: "Bob"})',
        'return', 'count(*)'
    ]
    string = """
        {   }  [   ]   (   )   {  [  ]  }  ({ }) {([ ])} {{{ }}} [[[ ]]] ((( ))) [{( )}]
        '{   }  [   ]   (   )   {  [  ]  }  ({ }) {([ ])} {{{ }}} [[[ ]]] ((( ))) [{( )}]'
        "{   }  [   ]   (   )   {  [  ]  }  ({ }) {([ ])} {{{ }}} [[[ ]]] ((( ))) [{( )}]"
        "{[  { } {{ [   ]   (   )  ( {  [  ((]  } (]]]]]]{{[(]0[ ({ }) {([ ])} {{{ }}} [[[ ]]] ((( ))) [{( )}] [[{(([[({{i"
    """
    assert tokenize(string) == [
        '{   }', '[   ]', '(   )', '{  [  ]  }', '({ })', '{([ ])}', '{{{ }}}', '[[[ ]]]', '((( )))', '[{( )}]',
        '\'{   }  [   ]   (   )   {  [  ]  }  ({ }) {([ ])} {{{ }}} [[[ ]]] ((( ))) [{( )}]\'',
        '"{   }  [   ]   (   )   {  [  ]  }  ({ }) {([ ])} {{{ }}} [[[ ]]] ((( ))) [{( )}]"',
        '"{[  { } {{ [   ]   (   )  ( {  [  ((]  } (]]]]]]{{[(]0[ ({ }) {([ ])} {{{ }}} [[[ ]]] ((( ))) [{( )}] [[{(([[({{i"'
    ]
    with raises(ValueError):
        tokenize('{')
    with raises(ValueError):
        tokenize('[')
    with raises(ValueError):
        tokenize('(')
    with raises(ValueError):
        tokenize('[(])')
    with raises(ValueError):
        tokenize('[{[(])}]')
    string = """
        ' '    ' " {[" }'     '  \\' " \\' " \\' \\'\\' \\\\'\\'
        "' '"    "' \\" {[\\" }'"     "'  \\' \\" \\' \\" \\' \\'\\' \\\\'\\'"
        " "    " ' {[' }"     "  \\" ' \\" ' \\" \\"\\" \\\\"\\"
        '" "'    '" \\' {[\\' }"'     '"  \\" \\' \\" \\' \\" \\"\\" \\\\"\\"'
    """
    assert tokenize(string) == [
        """' '""", """' " {[" }'""", """'  \\' " \\' " \\' \\'\\' \\\\'\\'""",
        '''"' '"''', '''"' \\" {[\\" }'"''', '''"'  \\' \\" \\' \\" \\' \\'\\' \\\\'\\'"''',
        '''" "''', '''" ' {[' }"''', '''"  \\" ' \\" ' \\" \\"\\" \\\\"\\"''',
        """'" "'""", """'" \\' {[\\' }"'""", """'"  \\" \\' \\" \\' \\" \\"\\" \\\\"\\"'"""
    ]
    with raises(ValueError):
        tokenize('\'')
    with raises(ValueError):
        tokenize('"')
    with raises(ValueError):
        tokenize('\'\'\'')
    with raises(ValueError):
        tokenize('"""')

def test_append(m):
    q = TNode.query
    assert q.string == 'match (instance:TNode) return instance'
    q = q.append('where instance.string = "foo"')
    assert q.string == 'match (instance:TNode) where instance.string = "foo" return instance'
    q = q.append('order by id(instance) desc')
    assert q.string == 'match (instance:TNode) where instance.string = "foo" return instance order by id(instance) desc'
    q = q.append('limit 10')
    assert q.string == 'match (instance:TNode) where instance.string = "foo" return instance order by id(instance) desc limit 10'
    q = q.append('skip 10')
    assert q.string == 'match (instance:TNode) where instance.string = "foo" return instance order by id(instance) desc skip 10'
    q = q.append('limit 10')
    assert q.string == 'match (instance:TNode) where instance.string = "foo" return instance order by id(instance) desc skip 10 limit 10'
    q = q.append('order by instance.string, id(instance) desc')
    assert q.string == 'match (instance:TNode) where instance.string = "foo" return instance order by instance.string, id(instance) desc'
    q = q.append('return instance.string, id(instance)')
    assert q.string == 'match (instance:TNode) where instance.string = "foo" return instance.string, id(instance)'
    q = q.append('skip 10 limit 10')
    assert q.string == 'match (instance:TNode) where instance.string = "foo" return instance.string, id(instance) skip 10 limit 10'
    q = q.append('order by instance.string, id(instance) desc')
    assert q.string == 'match (instance:TNode) where instance.string = "foo" return instance.string, id(instance) order by instance.string, id(instance) desc'
    q = q.append('limit 10')
    assert q.string == 'match (instance:TNode) where instance.string = "foo" return instance.string, id(instance) order by instance.string, id(instance) desc limit 10'
    q = q.append('and instance.integer = 1')
    assert q.string == 'match (instance:TNode) where instance.string = "foo" and instance.integer = 1 return instance.string, id(instance) order by instance.string, id(instance) desc limit 10'
    q = TNode.query
    assert q.string == 'match (instance:TNode) return instance'
    q = q.append('union match (instance:SubTNode) return instance')
    assert q.string == 'match (instance:TNode) return instance union match (instance:SubTNode) return instance'
    q = q.append('where instance.string = "foo"')
    assert q.string == 'match (instance:TNode) return instance union match (instance:SubTNode) where instance.string = "foo" return instance'
    q = q.append('return id(instance) limit 10')
    assert q.string == 'match (instance:TNode) return instance union match (instance:SubTNode) where instance.string = "foo" return id(instance) limit 10'
    q = q.append('skip 10 limit 10')
    assert q.string == 'match (instance:TNode) return instance union match (instance:SubTNode) where instance.string = "foo" return id(instance) skip 10 limit 10'
    q = q.append('union match (instance:IFieldNode) return instance')
    assert q.string == 'match (instance:TNode) return instance union match (instance:SubTNode) where instance.string = "foo" return id(instance) skip 10 limit 10 union match (instance:IFieldNode) return instance'
    q = TNode.query
    assert q.string == 'match (instance:TNode) return instance'
    q = q.append('where instance.string = "foo" return id(instance) order by id(instance) desc limit 10')
    assert q.string == 'match (instance:TNode) where instance.string = "foo" return id(instance) order by id(instance) desc limit 10'
    q = q.append('union all match (instance:TNode) where instance.string = "foo" return id(instance) order by id(instance) desc limit 10')
    assert q.string == 'match (instance:TNode) where instance.string = "foo" return id(instance) order by id(instance) desc limit 10 union all match (instance:TNode) where instance.string = "foo" return id(instance) order by id(instance) desc limit 10'

def test_elixir_compat(m):
    q = TNode.query
    assert q.string == 'match (instance:TNode) return instance'
    q = q.offset(0)
    assert q.string == 'match (instance:TNode) return instance skip 0'
    q = q.limit(10)
    assert q.string == 'match (instance:TNode) return instance skip 0 limit 10'
    q = q.offset(10)
    assert q.string == 'match (instance:TNode) return instance skip 10'
    q = q.limit(20)
    assert q.string == 'match (instance:TNode) return instance skip 10 limit 20'
    q = q.limit(30)
    assert q.string == 'match (instance:TNode) return instance skip 10 limit 30'
    q = q.append('return count(*)')
    assert q.string == 'match (instance:TNode) return count(*)'

    v1 = randint(0, 2**30)
    q = TNode.query.append('where instance.integer = {0} return instance'.format(v1))
    assert q.count() == 0
    assert q.first() is None
    with raises(QueryError):
        q.one()
    n1 = TNode(integer=v1)
    m.session.commit()
    assert q.count() == 1
    assert q.first() is n1
    assert q.one() is n1
    n2 = TNode(integer=v1)
    m.session.commit()
    assert q.count() == 2
    assert q.first() in (n1, n2)
    with raises(QueryError):
        q.one()

def test_get_by(m):
    v1 = randint(0, 2**30)
    n1 = TNode(integer=v1)
    m.session.commit()
    assert Node.get_by(integer=v1) is n1
    assert TNode.get_by(integer=v1) is n1
    assert SubTNode.get_by(integer=v1) is None
    m.session.clear()
    n1 = Node.get_by(integer=v1)
    assert isinstance(n1, TNode)
    assert n1.integer == v1
    assert TNode.get_by(integer=v1) is n1
    assert SubTNode.get_by(integer=v1) is None
