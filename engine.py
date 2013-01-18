from py2neo import neo4j, cypher

class Engine(object):

    def __init__(self, url):
        self.instance = neo4j.GraphDatabaseService(url)

    def execute(self, *args, **kwargs):
        return cypher.execute(self.instance, *args, **kwargs)
