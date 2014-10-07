from py2neo.neo4j import *
from py2neo import neo4j
import py2neo

if py2neo.__version__ in ('1.6.4',):

    """
    This restores the id property for consistency with previous versions.
    """
    neo4j._Entity.id = neo4j._Entity._id

    """
    This ensures consistent cypher result format for batches (see __hydrate()).
    Redefined in full since the name-mangled __hydrate makes it difficult to override cleanly.
    """
    from py2neo.neo4j import _hydrated

    class BatchResponse(object):

        @classmethod
        def __hydrate(cls, result, hydration_cache=None):
            body = result.get("body")
            if isinstance(body, dict):
                if has_all(body, CypherResults.signature):
                    return CypherResults._hydrated(body, hydration_cache)
                elif has_all(body, ("exception", "stacktrace")):
                    err = ServerException(body)
                    try:
                        CustomBatchError = type(err.exception, (BatchError,), {})
                    except TypeError:
                        # for Python 2.x
                        CustomBatchError = type(str(err.exception), (BatchError,), {})
                    raise CustomBatchError(err)
                else:
                    return _hydrated(body, hydration_cache)
            else:
                return _hydrated(body, hydration_cache)

        def __init__(self, result, raw=False, hydration_cache=None):
            self.id_ = result.get("id")
            self.uri = result.get("from")
            self.body = result.get("body")
            self.status_code = result.get("status", 200)
            self.location = URI(result.get("location"))
            if __debug__:
                batch_log.debug("<<< {{{0}}} {1} {2} {3}".format(self.id_, self.status_code, self.location, self.body))
            # We need to hydrate on construction to catch any errors in the batch
            # responses contained in the body
            if raw:
                self.__hydrated = None
            else:
                self.__hydrated = self.__hydrate(result, hydration_cache)

        @property
        def __uri__(self):
            return self.uri

        @property
        def hydrated(self):
            return self.__hydrated

    neo4j.BatchResponse = BatchResponse
    
    """
    This ensures that loaded paths contain the real relationships and not just abstract data.
    Also skips default init on hydration for performance reasons (_UnboundRelationship.cast()).
    """
    from py2neo.neo4j import _rel
    
    class Path(neo4j.Path):

        @classmethod
        def _hydrated(cls, data):
            path = cls()
            path._nodes = [Node(item) for item in  data["nodes"]]
            path._relationships = [Relationship(item) for item in data["relationships"]]
            return path

        def __init__(self, *args):
            if len(args) > 0:
                super(Path, self).__init__(*args)
            else:
                self._nodes = []
                self._relationships = []

    neo4j.Path = Path

else:
    raise ImportError("Untested version of py2neo ({0}), please check overrides.".format(py2neo.__version__))
