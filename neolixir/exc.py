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

"""Defines standard Neolixir exceptions and imports ``py2neo`` exceptions."""

import traceback
import overrides

from py2neo.error import GraphError
from py2neo.cypher import CypherError
from py2neo.batch import BatchError

EntityNotFoundException = GraphError.subcls('EntityNotFoundException')
NodeNotFoundException = GraphError.subcls('NodeNotFoundException')
RelationshipNotFoundException = GraphError.subcls('RelationshipNotFoundException')
EndNodeNotFoundException = GraphError.subcls('EndNodeNotFoundException')

DeadlockDetectedException = GraphError.subcls('DeadlockDetectedException')
GuardTimeoutException = GraphError.subcls('GuardTimeoutException')

__all__ = ['GraphError', 'CypherError', 'BatchError',
           'EntityNotFoundException', 'NodeNotFoundException',
           'RelationshipNotFoundException', 'EndNodeNotFoundException',
           'DeadlockDetectedException', 'GuardTimeoutException',
           'NeolixirError', 'CommitError', 'QueryError']

class NeolixirError(Exception):
    """Base class for all Neolixir exceptions."""
    pass

class CommitError(NeolixirError):
    """Triggered when an error occurred during session commit."""

    def __init__(self, exc_info, saved, pending):
        self.exc_info = exc_info
        msg = u''.join(traceback.format_exception(*exc_info))
        for job, response in saved:
            msg += u'\nSAVED: {0} /{1} {2} -> {3}'.format(job.method, job.target.uri_string, job.body, response)
        for job in pending:
            msg += u'\nPENDING: {0} /{1} {2}'.format(job.method, job.target.uri_string, job.body)
        super(CommitError, self).__init__(msg)

class QueryError(NeolixirError):
    """Exception class for Queries."""
    pass
