import threading
from py2neo import neo4j, cypher

engine = None

def get_engine():
    if instance is None:
        raise ValueError("Neo4j engine not initialized!")
    return engine.instance

class Engine(object):

    def __init__(self, url='http://localhost:7474/db/data/'):
        self.__threadlocal__ = threading.local()
        self.url = url

    @property
    def instance(self):
        try:
            return self.__threadlocal__.instance
        except AttributeError:
            self.__threadlocal__.instance = neo4j.GraphDatabaseService(self.url)
            return self.__threadlocal__.instance

    def execute(self, *args, **kwargs):
        return cypher.execute(self.instance, *args, **kwargs)
