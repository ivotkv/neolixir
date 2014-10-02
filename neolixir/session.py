import re
import sys
import threading
from copy import copy
from itertools import chain
from py2neo import neo4j
from exc import *

class Session(object):

    def __init__(self, metadata=None):
        self._threadlocal = threading.local()
        self.metadata = metadata

    def clear(self):
        self.batch.clear()
        self.nodes.clear()
        self.phantomnodes.clear()
        self.relmap.clear()
        self.propmap.clear()

    @property
    def committing(self):
        try:
            return self._threadlocal.committing
        except AttributeError:
            self._threadlocal.committing = False
            return self._threadlocal.committing

    @committing.setter
    def committing(self, value):
        self._threadlocal.committing = value

    @property
    def batch(self):
        try:
            return self._threadlocal.batch
        except AttributeError:
            self._threadlocal.batch = self.metadata.batch()
            return self._threadlocal.batch

    @property
    def nodes(self):
        try:
            return self._threadlocal.nodes
        except AttributeError:
            self._threadlocal.nodes = {}
            return self._threadlocal.nodes

    @property
    def phantomnodes(self):
        try:
            return self._threadlocal.phantomnodes
        except AttributeError:
            self._threadlocal.phantomnodes = set()
            return self._threadlocal.phantomnodes

    @property
    def relmap(self):
        try:
            return self._threadlocal.relmap
        except AttributeError:
            from relmap import RelMap
            self._threadlocal.relmap = RelMap()
            return self._threadlocal.relmap

    @property
    def propmap(self):
        try:
            return self._threadlocal.propmap
        except AttributeError:
            from propmap import PropMap
            self._threadlocal.propmap = PropMap()
            return self._threadlocal.propmap

    def __len__(self):
        return self.count

    @property
    def count(self):
        return len(self.nodes) + len(self.phantomnodes) + len(self.relmap)

    @property
    def new(self):
        return len(self.phantomnodes) + len(self.relmap._phantoms)

    @property
    def dirty(self):
        return sum((1 for x in chain(self.nodes.itervalues(), self.relmap.iterpersisted()) if x.is_dirty()))

    def is_dirty(self):
        return self.new + self.dirty > 0

    def add(self, entity):
        from relationship import Relationship
        if isinstance(entity, Relationship):
            self.relmap.add(entity)
        else:
            if entity.is_phantom():
                self.phantomnodes.add(entity)
            else:
                self.phantomnodes.discard(entity)
                self.nodes[entity.id] = entity
        entity._session = self

    def get(self, value):
        if isinstance(value, neo4j.Node):
            return self.nodes.get(value.id)
        elif isinstance(value, neo4j.Relationship):
            return self.relmap.get(value)
        else:
            return None

    def expunge(self, entity):
        from relationship import Relationship
        if isinstance(entity, Relationship):
            self.relmap.remove(entity)
        else:
            for rel in list(self.relmap.node.get(entity, [])):
                self.expunge(rel)
            self.phantomnodes.discard(entity)
            self.nodes.pop(entity.id, None)
        self.propmap.remove(entity)
        entity._session = None

    def rollback(self):
        self.batch.clear()
        self.propmap.clear()
        self.relmap.rollback()
        self.phantomnodes.clear()
        for node in self.nodes.itervalues():
            node.rollback()

    def commit(self, batched=True, batch_size=100):
        self.committing = True

        from node import Node
        from relationship import Relationship

        retry = True
        while retry:
            retry = False
            try:
                self._commit(batched=batched, batch_size=batch_size)
            except CommitError as e:
                error = unicode(e.trace[-1])
                if re.search('DeadlockDetectedException', error):
                    retry = True
                    continue
                elif re.search('EntityNotFoundException', error):
                    if re.search(r'Node \d+ not found', error):
                        id = re.sub(r'^.*Node (\d+) not found.*$', r'\1', error)
                        if id.isdigit():
                            node = Node(int(id))
                            if node.is_deleted():
                                node.expunge()
                                retry = True
                                continue
                    elif re.search(r'Relationship \d+ not found', error):
                        id = re.sub(r'^.*Relationship (\d+) not found.*$', r'\1', error)
                        if id.isdigit():
                            rel = Relationship(int(id))
                            if rel.is_deleted():
                                rel.expunge()
                                retry = True
                                continue
                elif re.search('ResourceNotFound', error):
                    if re.search(r'/node/\d+', error):
                        id = re.sub(r'^.*/node/(\d+)\D*$', r'\1', error)
                        if id.isdigit():
                            node = Node(int(id))
                            if node.is_deleted():
                                node.expunge()
                                retry = True
                                continue
                    elif re.search(r'/relationship/\d+', error):
                        id = re.sub(r'^.*/relationship/(\d+)\D*$', r'\1', error)
                        if id.isdigit():
                            rel = Relationship(int(id))
                            if rel.is_deleted():
                                rel.expunge()
                                retry = True
                                continue
                raise e

        self.committing = False

    def _commit(self, batched=True, batch_size=100):
        if batched:
            # clear batch just in case
            self.batch.clear()

            # get data to be saved
            nodes = list(chain(self.phantomnodes, self.nodes.itervalues()))
            rels = list(self.relmap)

            saved = []
            pending = []

            try:
                # submit nodes
                count = 0
                for node in nodes:
                    if node.is_phantom() or node.is_dirty():
                        self.batch.save(node)
                        count += 1
                    if batch_size and count % batch_size == 0:
                        pending = copy(self.batch.requests)
                        responses = self.batch.submit()
                        for idx, request in enumerate(pending):
                            saved.append((request, responses[idx]))
                        pending = []
                pending = copy(self.batch.requests)
                responses = self.batch.submit()
                for idx, request in enumerate(pending):
                    saved.append((request, responses[idx]))
                pending = []

                # submit rels
                count = 0
                for rel in rels:
                    if rel.is_phantom() or rel.is_dirty():
                        self.batch.save(rel)
                        count += 1
                    if batch_size and count % batch_size == 0:
                        pending = copy(self.batch.requests)
                        responses = self.batch.submit()
                        for idx, request in enumerate(pending):
                            saved.append((request, responses[idx]))
                        pending = []
                pending = copy(self.batch.requests)
                responses = self.batch.submit()
                for idx, request in enumerate(pending):
                    saved.append((request, responses[idx]))
                pending = []

            except:
                raise CommitError(sys.exc_info(), saved, pending)

        else:
            while len(self.phantomnodes) > 0:
                self.phantomnodes.pop().save()
            for entity in list(chain(self.nodes.itervalues(), self.relmap)):
                entity.save()
