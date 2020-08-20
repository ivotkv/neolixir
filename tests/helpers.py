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

from neolixir.relmap import RelView
from utils import *

def create_out_of_session(m, entity):

    assert entity.is_phantom()
    entity.expunge()

    @checked_thread
    def run(m, entity):
        m.session.add(entity)
        m.session.commit()
        return entity.id

    return run(m, entity)

def update_out_of_session(m, entity, properties=None):

    assert not entity.is_phantom()
    if properties == None:
        properties = entity.properties

    @checked_thread
    def run(m, entity, properties):
        entity = entity.cls.get(entity.id)
        entity.properties.update(properties)
        m.session.commit()
        return m.session.dirty == 0

    return run(m, entity, properties)

def delete_out_of_session(m, entity):

    assert not entity.is_phantom()

    @checked_thread
    def run(m, entity):
        entity = entity.cls.get(entity.id)
        entity.delete()
        m.session.commit()
        return entity not in m.session

    return run(m, entity)

def append_out_of_session(m, n1, relname, n2):

    assert not n1.is_phantom()
    assert isinstance(relname, basestring)
    assert isinstance(getattr(n1, relname, None), RelView)
    assert not n2.is_phantom()

    @checked_thread
    def run(m, n1, relname, n2):
        n1 = n1.cls.get(n1.id)
        n2 = n2.cls.get(n2.id)
        rel = getattr(n1, relname).append(n2)
        m.session.commit()
        return rel.id if rel else None

    return run(m, n1, relname, n2)

def remove_out_of_session(m, n1, relname, n2):

    assert not n1.is_phantom()
    assert isinstance(relname, basestring)
    assert isinstance(getattr(n1, relname, None), RelView)
    assert not n2.is_phantom()

    @checked_thread
    def run(m, n1, relname, n2):
        n1 = n1.cls.get(n1.id)
        n2 = n2.cls.get(n2.id)
        relview = getattr(n1, relname)
        if n2 in relview:
            count = len(relview)
            relview.remove(n2)
            m.session.commit()
            return len(relview) == count - 1
        else:
            return False

    return run(m, n1, relname, n2)
