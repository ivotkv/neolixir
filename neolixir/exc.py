"""Defines standard Neolixir exceptions and imports ``py2neo`` exceptions."""

try:
    from py2neo.rest import BadRequest, ResourceNotFound, ResourceConflict, SocketError
except ImportError:
    BadRequest = Exception
    ResourceNotFound = Exception
    ResourceConflict = Exception
    SocketError = Exception
from py2neo.cypher import CypherError

__all__ = ['NeolixirError', 'CommitError',
           'QueryError', 'NoResultFound', 'MultipleResultsFound',
           'CypherError','BadRequest', 'ResourceNotFound',
           'ResourceConflict', 'SocketError']

class NeolixirError(Exception):
    """Base class for all Neolixir exceptions."""
    pass

class CommitError(NeolixirError):
    """Triggered when an error occurred during session commit."""

    def __init__(self, e, saved, pending):
        msg = u'{0}: {1}'.format(e.__class__.__name__, e)
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
