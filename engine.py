import threading
from py2neo import neo4j, cypher

class OperationalError(Exception):
    pass

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

    def execute(self, *args, **kwargs):
        return cypher.execute(self.instance, *args, **kwargs)
