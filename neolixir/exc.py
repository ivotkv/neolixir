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
