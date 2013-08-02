from types import FunctionType
from inspect import getargspec
from itertools import chain, ifilter, imap
from py2neo import neo4j
from metadata import metadata as m
from relationship import Relationship
from node import Node
from util import IN, OUT

class RelList(list):

    def __init__(self, direction, *args, **kwargs):
        super(RelList, self).__init__(*args, **kwargs)
        self.direction = direction
        self.nodes = {}
        for rel in self:
            node = self.nodefunc(rel)
            if node not in self.nodes:
                self.nodes[node] = set([rel])
            else:
                self.nodes[node].add(rel)

    def nodefunc(self, rel):
        return rel.end if self.direction == OUT else rel.start

    def rel(self, node):
        return self.nodes.get(node, set())

    def append(self, rel):
        super(RelList, self).append(rel)
        node = self.nodefunc(rel)
        if node not in self.nodes:
            self.nodes[node] = set([rel])
        else:
            self.nodes[node].add(rel)

    def remove(self, rel):
        try:
            super(RelList, self).remove(rel)
        except ValueError:
            pass
        else:
            node = self.nodefunc(rel)
            if node in self.nodes:
                self.nodes[node].discard(rel)
                if len(self.nodes[node]) == 0:
                    del self.nodes[node]

class RelMap(object):

    def __init__(self):
        self._ids = {}
        self._phantoms = set()
        self.node = {}
        self.start = {}
        self.end = {}

    def clear(self):
        self._ids.clear()
        self._phantoms.clear()
        self.node.clear()
        self.start.clear()
        self.end.clear()

    def _track(self, rel):
        if rel.id is not None:
            self._phantoms.discard(rel)
            self._ids[rel.id] = rel
        else:
            self._phantoms.add(rel)
        rel._relmap = self

    def _untrack(self, rel):
        self._ids.pop(rel.id, None)
        self._phantoms.discard(rel)
        rel._relmap = None

    def _map(self, rel):
        if not self.node.has_key(rel.start):
            self.node[rel.start] = set()
        self.node[rel.start].add(rel)

        if not self.node.has_key(rel.end):
            self.node[rel.end] = set()
        self.node[rel.end].add(rel)

        if not self.start.has_key((rel.start, rel.type)):
            self.start[(rel.start, rel.type)] = RelList(OUT)
        self.start[(rel.start, rel.type)].append(rel)

        if not self.end.has_key((rel.end, rel.type)):
            self.end[(rel.end, rel.type)] = RelList(IN)
        self.end[(rel.end, rel.type)].append(rel)

    def _unmap(self, rel):
        try:
            self.node[rel.start].discard(rel)
            self.node[rel.end].discard(rel)
            self.start[(rel.start, rel.type)].remove(rel)
            self.end[(rel.end, rel.type)].remove(rel)
        except KeyError:
            pass

    def add(self, rel):
        self._track(rel)
        self.update(rel)

    def update(self, rel):
        if not rel.is_deleted():
            self._map(rel)
        else:
            self._unmap(rel)

    def remove(self, rel):
        self._untrack(rel)
        self._unmap(rel)

    def get(self, value):
        if isinstance(value, int):
            return self._ids.get(value)
        elif isinstance(value, neo4j.Relationship):
            return self._ids.get(value.id)
        else:
            return None

    def __len__(self):
        return len(self._ids) + len(self._phantoms)

    def __iter__(self):
        return chain(self._ids.itervalues(), iter(self._phantoms))

    def iterphantoms(self):
        return iter(self._phantoms)

    def iterpersisted(self):
        return self._ids.itervalues()

    def rollback(self):
        try:
            while True:
                rel = self._phantoms.pop()
                self._unmap(rel)
        except KeyError:
            pass
        for rel in self._ids.itervalues():
            rel.rollback()

    def load_rels(self, node, direction, type, other=None):
        # other=False will prevent the load
        if not other is False and not node.is_phantom():
            params = {'node_id': node.id}
            q = 'start n=node({node_id})'

            if other is not None:
                params['other_id'] = other if isinstance(other, int) else other.id
                q += ', o=node({other_id})'

            if direction is OUT:
                q += ' match n-[r:{0}]->o return r, o'.format(type)
            else:
                q += ' match n<-[r:{0}]-o return r, o'.format(type)

            m.cypher(q, params=params)

class RelView(object):

    __default_cls__ = Relationship

    def __init__(self, owner, direction, type_, target=None, multiple=False, preloaded=False):
        self.relmap = m.session.relmap
        self.owner = owner
        self.direction = direction
        self.type = getattr(type_, '__rel_type__', type_)
        self.cls = type_ if isinstance(type_, type) else self.__default_cls__
        self.target = target
        self.multiple = multiple if target is None else False
        self.preloaded = preloaded
        self._noload = 0

    def load(self):
        self.relmap.load_rels(self.owner, self.direction, self.type, other=self.get_target())

    def get_target(self):
        if hasattr(self.target, '__call__'):
            if isinstance(self.target, FunctionType) and len(getargspec(self.target).args) == 1:
                return self.target(self.owner)
            else:
                return self.target()
        else:
            return self.target

    @property
    def data(self):
        try:
            return self._data
        except AttributeError:
            if not self.preloaded:
                self.load()
            if self.direction == OUT:
                if not self.relmap.start.has_key((self.owner, self.type)):
                    self.relmap.start[(self.owner, self.type)] = RelList(OUT)
                self._data = self.relmap.start[(self.owner, self.type)]
            else:
                if not self.relmap.end.has_key((self.owner, self.type)):
                    self.relmap.end[(self.owner, self.type)] = RelList(IN)
                self._data = self.relmap.end[(self.owner, self.type)]
            return self._data

    # using 'with' will prevent preloading within its context
    def __enter__(self):
        if not hasattr(self, '_data') and self.preloaded is False or self._noload > 0:
            self._noload += 1
            self.preloaded = True

    def __exit__(self, exc_type, exc_value, traceback):
        if self._noload == 1:
            self._noload = 0
            self.preloaded = False
            if hasattr(self, '_data'):
                delattr(self, '_data')
        elif self._noload > 1:
            self._noload -= 1

    def nodefunc(self, value):
        if isinstance(value, Relationship):
            return value.end if self.direction == OUT else value.start
        elif isinstance(value, Node):
            return value
        else:
            raise TypeError("unexpected type: " + value.__class__.__name__)

    def relfunc(self, value):
        if isinstance(value, Relationship):
            return value
        else:
            other = Node(value)
            if other is not None:
                if self.direction == OUT:
                    return self.cls((self.owner, self.type, other))
                else:
                    return self.cls((other, self.type, self.owner))
            else:
                raise ValueError("could not find other Node")

    def __iter__(self):
        return imap(self.nodefunc, self.data)

    def __contains__(self, item):
        if isinstance(item, Relationship):
            return item in self.data
        else:
            return item in iter(self)

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        return "[{0}]".format(", ".join(imap(repr, iter(self))))

    def __getitem__(self, key):
        return self.nodefunc(self.data[key])

    def __delitem__(self, key):
        self.data[key].delete()

    def sorted(self):
        return map(self.nodefunc, sorted(self.data,
                                          cmp=self.cls.__sort_cmp__,
                                          key=self.cls.__sort_key__))

    def reversed(self):
        return map(self.nodefunc, sorted(self.data,
                                          cmp=self.cls.__sort_cmp__,
                                          key=self.cls.__sort_key__,
                                          reverse=True))

    def iterrels(self):
        return iter(self.data)

    def rels(self):
        return self.data

    def node(self, rel):
        return self.nodefunc(rel)

    def rel(self, node):
        rels = list(self.data.rel(node))
        if self.multiple:
            return rels
        elif rels:
            return rels[0]
        else:
            return None

    def append(self, value):
        if self.multiple or value not in self:
            return self.relfunc(value)
        return None

    def remove(self, value):
        if isinstance(value, Node):
            for rel in list(self.data.rel(value)):
                rel.delete()
        elif isinstance(value, Relationship) and value in self:
            value.delete()