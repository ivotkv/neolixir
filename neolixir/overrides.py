import py2neo

if py2neo.__version__ in ('1.6.4',):
    
    """
    This ensures that loaded paths contain the real relationships and not just abstract data.
    Also skips default init on hydration for performance reasons (_UnboundRelationship.cast()).
    """
    from py2neo.neo4j import *
    from py2neo.neo4j import _rel
    from py2neo import neo4j
    
    class Path(neo4j.Path):

        @classmethod
        def _hydrated(cls, data):
            path = cls()
            path._nodes = [Node(item) for item in data["nodes"]]
            path._relationships = [Relationship(item) for item in data["relationships"]]
            return path

        def __init__(self, *args):
            if len(args) > 0:
                super(Path, self).__init__(*args)
            else:
                self._nodes = []
                self._relationships = []

    neo4j.Path = Path

elif py2neo.__version__ in ('2.0.beta',):

    """
    This restores the id property for consistency with previous versions.
    """
    from py2neo.core import Node, Relationship
    Node.id = Node._id
    Relationship.id = Relationship._id

    """
    This ensures consistent cypher result format for batches (see __hydrate()).
    Redefined in full since the name-mangled __hydrate makes it difficult to override cleanly.
    """
    from py2neo.batch.core import JobResult, GraphError, BatchError, ustr, raise_from

    def hydrate(cls, data, batch):
        graph = getattr(batch, "graph", None)
        job_id = data["id"]
        uri = data["from"]
        status_code = data.get("status")
        location = data.get("location")
        if graph is None or batch[job_id].raw_result:
            body = data.get("body")
        else:
            body = None
            try:
                body = graph.hydrate(data.get("body"))
            except GraphError as error:
                message = "Batch job %s failed with %s\n%s" % (
                    job_id, error.__class__.__name__, ustr(error))
                raise_from(BatchError(message, batch, job_id, status_code, uri, location), error)
        return cls(batch, job_id, uri, status_code, location, body)

    JobResult.hydrate = classmethod(hydrate)

else:
    raise ImportError("Untested version of py2neo ({0}), please check overrides.".format(py2neo.__version__))
