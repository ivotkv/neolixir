from py2neo import neo4j, cypher
from utils import ThreadLocalRegistry as TLR

class Engine(object):

    def __init__(self, url='http://localhost:7474/db/data/'):
        self.url = url
        self.threadsafe = TLR(url, instance=lambda url: neo4j.GraphDatabaseService(url))

    def execute(self, *args, **kwargs):
        return cypher.execute(self.threadsafe.instance, *args, **kwargs)
