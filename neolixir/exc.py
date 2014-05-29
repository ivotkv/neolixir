"""Defines standard Neolixir exceptions and imports ``py2neo`` exceptions."""

try:
    from py2neo.rest import BadRequest, ResourceNotFound, ResourceConflict, SocketError
except ImportError:
    BadRequest = Exception
    ResourceNotFound = Exception
    ResourceConflict = Exception
    SocketError = Exception
from py2neo.cypher import CypherError

__all__ = ['NeolixirError', 'QueryError', 'NoResultFound',
           'MultipleResultsFound', 'CypherError','BadRequest',
           'ResourceNotFound', 'ResourceConflict', 'SocketError']

class NeolixirError(Exception):
    """Base class for all Neolixir exceptions."""
    pass

class QueryError(NeolixirError):
    """Base class for all Neolixir query exceptions."""
    pass

class NoResultFound(QueryError):
    """Triggered when results were expected but none were found."""
    pass

class MultipleResultsFound(QueryError):
    """Triggered when a single result was expected but more were found."""
    pass
