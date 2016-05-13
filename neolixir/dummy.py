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

class DummyEntity(object):

    __slots__ = ['id', 'properties']

    def __init__(self, id, properties=None):
        self.id = id
        self.properties = properties or {}

    def __repr__(self):
        return "<{0} (0x{1:x}): ({2}) {3}>".format(self.__class__.__name__, id(self),
                                                   self.id, self.properties)

class DummyNode(DummyEntity):

    __slots__ = []

class DummyRelationship(DummyEntity):

    __slots__ = ['start_node', 'type', 'end_node']
    
    def __init__(self, id, start_node, type, end_node, properties=None):
        self.id = id
        self.start_node = start_node
        self.type = type
        self.end_node = end_node
        self.properties = properties or {}

    def __repr__(self):
        return "<{0} (0x{1:x}): ({2})-[{3}:{4}]->({5}) {6}>".format(self.__class__.__name__, id(self),
                                                                    getattr(self.start_node, 'id', None),
                                                                    self.id, self.type, 
                                                                    getattr(self.end_node, 'id', None),
                                                                    self.properties)
