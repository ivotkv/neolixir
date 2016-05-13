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

import re
import sys
import threading
from copy import copy
from itertools import chain
import overrides
from py2neo import neo4j
from dummy import DummyEntity, DummyNode, DummyRelationship
from exc import *

class Session(object):

    def __init__(self, metadata=None):
        self._threadlocal = threading.local()
        self.metadata = metadata

    def clear(self):
        self.batch.clear()
        self.events.clear()
        self.nodes.clear()
        self.phantomnodes.clear()
        self.relmap.clear()
        self.propmap.clear()
        neo4j.Node.cache.clear()
        neo4j.Relationship.cache.clear()
        neo4j.Rel.cache.clear()

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
    def events(self):
        try:
            return self._threadlocal.events
        except AttributeError:
            from observable import SessionEvents
            self._threadlocal.events = SessionEvents()
            return self._threadlocal.events

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

    def __contains__(self, item):
        from node import Node
        if isinstance(item, Node):
            if item.is_phantom():
                return item in self.phantomnodes
            else:
                return item in self.nodes.itervalues()
        else:
            return item in self.relmap

    def __iter__(self):
        return chain(self.nodes.itervalues(), self.phantomnodes, self.relmap)

    def __len__(self):
        return len(self.nodes) + len(self.phantomnodes) + len(self.relmap)

    @property
    def count(self):
        return self.__len__()

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
        if isinstance(value, (DummyNode, neo4j.Node)):
            return self.nodes.get(value.id)
        elif isinstance(value, (DummyRelationship, neo4j.Relationship)):
            return self.relmap.get(value)
        else:
            return None

    def expunge(self, entity):
        from relationship import Relationship
        if isinstance(entity, Relationship):
            self.relmap.remove(entity)
            if entity._entity is not None and not isinstance(entity._entity, DummyEntity):
                neo4j.Relationship.cache.pop(entity._entity.uri, None)
                neo4j.Rel.cache.pop(entity._entity.uri, None)
        else:
            for rel in list(self.relmap.node.get(entity, [])):
                self.expunge(rel)
            self.phantomnodes.discard(entity)
            self.nodes.pop(entity.id, None)
            if entity._entity is not None and not isinstance(entity._entity, DummyEntity):
                neo4j.Node.cache.pop(entity._entity.uri, None)
        self.propmap.remove(entity)
        entity._session = None

    def rollback(self):
        self.batch.clear()
        self.events.clear()
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
        max_retry = 5

        while retry and max_retry > 0:

            retry = False

            try:
                self._commit(batched=batched, batch_size=batch_size)

            except CommitError as e:
                exc = e.exc_info[1]

                if isinstance(exc, BatchError) and exc.status_code == 404:
                    if re.match(r'^node/\d+($|/.*$)', exc.uri):
                        id = re.sub(r'^node/(\d+)($|/.*$)', r'\1', exc.uri)
                        if id.isdigit():
                            node = Node.get(int(id))
                            if node.is_deleted():
                                node.expunge()
                                retry = True
                                continue
                    elif re.match(r'^relationship/\d+($|/.*$)', exc.uri):
                        id = re.sub(r'^relationship/(\d+)($|/.*$)', r'\1', exc.uri)
                        if id.isdigit():
                            rel = Relationship.get(int(id))
                            if rel.is_deleted():
                                rel.expunge()
                                retry = True
                                continue

                elif isinstance(exc, BatchError):
                    if isinstance(exc.__cause__, EntityNotFoundException):
                        try:
                            entity = exc.batch.jobs[exc.job_id].entity
                            if entity.is_deleted():
                                entity.expunge()
                                retry = True
                                continue
                        except (IndexError, AttributeError):
                            pass

                    # for the rest of the handlers, use the cause directly
                    exc = exc.__cause__

                if isinstance(exc, DeadlockDetectedException):
                    retry = True
                    max_retry -= 1
                    continue

                elif isinstance(exc, GuardTimeoutException):
                    retry = True
                    max_retry = 0
                    continue

                elif isinstance(exc, EntityNotFoundException):
                    error = unicode(exc)
                    if re.search(r'Node \d+ not found', error):
                        id = re.sub(r'^.*Node (\d+) not found.*$', r'\1', error)
                        if id.isdigit():
                            node = Node.get(int(id))
                            if node.is_deleted():
                                node.expunge()
                                retry = True
                                continue
                    elif re.search(r'Relationship \d+ not found', error):
                        id = re.sub(r'^.*Relationship (\d+) not found.*$', r'\1', error)
                        if id.isdigit():
                            rel = Relationship.get(int(id))
                            if rel.is_deleted():
                                rel.expunge()
                                retry = True
                                continue

                raise e

        self.events.fire_committed()
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
                count = len(self.batch.jobs)
                for node in nodes:
                    if node.is_phantom() or node.is_dirty():
                        self.batch.save(node)
                        if len(self.batch.jobs) > count:
                            self.batch.jobs[-1].entity = node
                            count += 1
                    if batch_size and count % batch_size == 0:
                        pending = copy(self.batch.jobs)
                        responses = self.batch.submit()
                        for idx, job in enumerate(pending):
                            saved.append((job, responses[idx]))
                        pending = []
                pending = copy(self.batch.jobs)
                responses = self.batch.submit()
                for idx, job in enumerate(pending):
                    saved.append((job, responses[idx]))
                pending = []

                # submit rels
                count = len(self.batch.jobs)
                for rel in rels:
                    if rel.is_phantom() or rel.is_dirty():
                        self.batch.save(rel)
                        if len(self.batch.jobs) > count:
                            self.batch.jobs[-1].entity = rel
                            count += 1
                    if batch_size and count % batch_size == 0:
                        pending = copy(self.batch.jobs)
                        responses = self.batch.submit()
                        for idx, job in enumerate(pending):
                            saved.append((job, responses[idx]))
                        pending = []
                pending = copy(self.batch.jobs)
                responses = self.batch.submit()
                for idx, job in enumerate(pending):
                    saved.append((job, responses[idx]))
                pending = []

            except:
                raise CommitError(sys.exc_info(), saved, pending)

        else:
            while len(self.phantomnodes) > 0:
                self.phantomnodes.pop().save()
            for entity in list(chain(self.nodes.itervalues(), self.relmap)):
                entity.save()
