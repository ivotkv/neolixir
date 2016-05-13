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

import threading
from itertools import ifilter
from utils import classproperty
import overrides
from py2neo import neo4j
from py2neo.core import Graph
from py2neo.legacy.core import LegacyResource
from session import Session
from dummy import DummyNode, DummyRelationship
from fast import fast_cypher

__all__ = ['metadata']

class MetaData(object):

    def __init__(self, url='http://localhost:7474/db/data/'):
        self.url = url
        self.session = Session(metadata=self)
        self.classes = {}

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        self._url = url
        self._threadlocal = threading.local()

    @property
    def host_port(self):
        return self.url.split('//')[-1].split('/')[0]

    @property
    def graph(self):
        try:
            return self._threadlocal.graph
        except AttributeError:
            self._threadlocal.graph = Graph(self.url)
            return self._threadlocal.graph

    @property
    def version(self):
        return self.graph.neo4j_version

    @property
    def legacy(self):
        try:
            return self._threadlocal.legacy
        except AttributeError:
            self._threadlocal.legacy = LegacyResource(self.url)
            return self._threadlocal.legacy

    def authenticate(self, username, password):
        try:
            from py2neo import authenticate
            authenticate(self.host_port, username, password)
            return True
        except ImportError:
            return False

    def change_password(self, username, password, new_password):
        try:
            from py2neo.password import UserManager
            um = UserManager.for_user(self.graph.service_root, username, password)
            return um.password_manager.change(new_password)
        except ImportError:
            return False

    def add(self, cls):
        self.classes.setdefault(cls.__name__, cls)

    def get(self, name):
        return self.classes.get(name)

    def clear(self):
        self.session = Session(metadata=self)
        self.classes = {}

    def cypher(self, query, params=None, automap=True, fast=False):
        if fast:
            results = fast_cypher(self, query, params=params)
        else:
            results = [list(record) for record in self.graph.cypher.execute(query, params or {})]

        if automap:
            results = self.automap(results, mapRels=False)
            results = self.automap(results, mapRels=True)

        return results

    def batch(self):
        from batch import WriteBatch
        return WriteBatch(self.graph, self)

    @classmethod
    def automap(cls, data, mapRels=True):
        from node import Node
        from relationship import Relationship

        mapped = []

        for item in data:

            if isinstance(item, (DummyNode, neo4j.Node)):
                mapped.append(Node.get(item))

            elif isinstance(item, (DummyRelationship, neo4j.Relationship)):
                if mapRels:
                    mapped.append(Relationship.get(item))
                else:
                    mapped.append(item)

            elif isinstance(item, list):
                mapped.append(cls.automap(item, mapRels=mapRels))

            elif isinstance(item, neo4j.Path):
                path = []
                for i, rel in enumerate(item.relationships):
                    path.append(Node.get(item.nodes[i]))
                    if mapRels:
                        path.append(Relationship.get(rel))
                    else:
                        path.append(rel)
                path.append(Node.get(item.nodes[-1]))
                mapped.append(path)

            else:
                mapped.append(item)

        return mapped

    def init(self, reset=False):
        from node import Node

        #TODO: create label indexes as needed

metadata = MetaData()
