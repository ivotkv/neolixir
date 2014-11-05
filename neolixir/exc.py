"""Defines standard Neolixir exceptions and imports ``py2neo`` exceptions."""

import traceback
import overrides

from py2neo.core import ClientError, ServerError
BadRequest = ClientError
ResourceNotFound = ClientError
ResourceConflict = ClientError
from py2neo.cypher import CypherError

__all__ = ['NeolixirError', 'CommitError',
           'QueryError', 'NoResultFound', 'MultipleResultsFound',
           'CypherError','BadRequest', 'ResourceNotFound',
           'ResourceConflict']

class NeolixirError(Exception):
    """Base class for all Neolixir exceptions."""
    pass

class CommitError(NeolixirError):
    """Triggered when an error occurred during session commit."""

    def __init__(self, exc_info, saved, pending):
        self.trace = traceback.format_exception(*exc_info)
        msg = u''.join(self.trace)
        for request, response in saved:
            msg += u'\nSAVED: {0} {1} {2} -> {3}'.format(request.method, request.uri, request.body, response)
        for request in pending:
            msg += u'\nPENDING: {0} {1} {2}'.format(request.method, request.uri, request.body)
        super(CommitError, self).__init__(msg)

class QueryError(NeolixirError):
    """Base class for all Neolixir query exceptions."""
    pass

class NoResultFound(QueryError):
    """Triggered when results were expected but none were found."""
    pass

class MultipleResultsFound(QueryError):
    """Triggered when a single result was expected but more were found."""
    pass
