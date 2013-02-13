from py2neo.rest import BadRequest, ResourceNotFound, ResourceConflict, SocketError
from py2neo.cypher import CypherError

__all__ = ['BadRequest', 'ResourceNotFound', 'ResourceConflict', 'SocketError',
           'CypherError', 'NeolixirError', 'QueryError', 'NoResultFound',
           'MultipleResultsFound']

class NeolixirError(Exception):
    pass

class QueryError(NeolixirError):
    pass

class NoResultFound(QueryError):
    pass

class MultipleResultsFound(QueryError):
    pass
