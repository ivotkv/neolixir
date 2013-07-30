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
            self.nodes[self._nodefunc(rel)] = rel

    def _nodefunc(self, rel):
        return rel.end if self.direction == OUT else rel.start

    def rel(self, node):
        return self.nodes.get(node, None)

    def append(self, rel):
        if rel not in self:
            super(RelList, self).append(rel)
            self.nodes[self._nodefunc(rel)] = rel

    def remove(self, rel):
        try:
            super(RelList, self).remove(rel)
            del self.nodes[self._nodefunc(rel)]
        except ValueError:
            pass

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

    def load_rels(self, node, direction, type):
        if not node.is_phantom():
            q = 'start n=node({node_id})'
            if direction is OUT:
                q += ' match n-[r:{0}]->o return r, o'.format(type)
            else:
                q += ' match n<-[r:{0}]-o return r, o'.format(type)

            m.cypher(q, params={'node_id': node.id})

class RelView(object):

    __default_cls__ = Relationship

    def __init__(self, owner, direction, type_, preloaded=False):
        self.relmap = m.session.relmap
        self.owner = owner
        self.direction = direction
        self.type = getattr(type_, '__rel_type__', type_)
        self.cls = type_ if isinstance(type_, type) else self.__default_cls__
        self.preloaded = preloaded

    def load(self):
        self.relmap.load_rels(self.owner, self.direction, self.type)

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
        if not hasattr(self, '_data') and self.preloaded is False:
            self._noload = True
            self.preloaded = True

    def __exit__(self, exc_type, exc_value, traceback):
        if getattr(self, '_noload', False):
            self._noload = False
            self.preloaded = False
            delattr(self, '_data')

    def _nodefunc(self, rel):
        return rel.end if self.direction == OUT else rel.start

    def _relfunc(self, value):
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
        return imap(self._nodefunc, self.data)

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
        return self._nodefunc(self.data[key])

    def __delitem__(self, key):
        self.data[key].delete()

    def sorted(self):
        return map(self._nodefunc, sorted(self.data,
                                          cmp=self.cls.__sort_cmp__,
                                          key=self.cls.__sort_key__))

    def reversed(self):
        return map(self._nodefunc, sorted(self.data,
                                          cmp=self.cls.__sort_cmp__,
                                          key=self.cls.__sort_key__,
                                          reverse=True))

    def iterrels(self):
        return iter(self.data)

    def rels(self):
        return self.data

    def node(self, rel):
        return self._nodefunc(rel)

    def rel(self, node):
        return self.data.rel(node)

    def append(self, value):
        if value not in self:
            return self._relfunc(value)
        return None

    def remove(self, value):
        if value in self:
            if not isinstance(value, Relationship):
                value = self.data.rel(value)
            value.delete()
