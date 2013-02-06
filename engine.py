import threading
from py2neo import neo4j, cypher

class Engine(object):

    def __init__(self, url='http://localhost:7474/db/data/', metadata=None):
        self._threadlocal = threading.local()
        self._metadata = metadata
        self.url = url

    @property
    def instance(self):
        try:
            return self._threadlocal.instance
        except AttributeError:
            self._threadlocal.instance = neo4j.GraphDatabaseService(self.url)
            return self._threadlocal.instance

    def batch(self):
        return WriteBatch(self.instance)

    def cypher(self, *args, **kwargs):
        return cypher.execute(self.instance, *args, **kwargs)[0]

class WriteBatch(neo4j.WriteBatch):

    def cypher(self, query, params=None):
        self._post(self._cypher_uri, {"query": query, "params": params or {}})

    def _resolve(self, data, status=200, id_=None):
        # NOTE: this is a hacky workaround for arbitrary cypher queries
        # TODO: should not rely on the AssertionError
        try:
            return [item for item in [self._graph_db._resolve(data, status, id_)] if item is not None]
        except AssertionError:
            return [self._graph_db._resolve(item, status, id_) for row in data["data"] for item in row]

    def submit(self):
        # NOTE: copy of original changed to use batch's _resolve
        return [
            self._resolve(response.body, response.status, id_=response.id)
            for response in self._submit()
        ]
