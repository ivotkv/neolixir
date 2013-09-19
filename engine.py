import threading
from py2neo import neo4j, cypher

class Engine(object):

    def __init__(self, url='http://localhost:7474/db/data/', metadata=None):
        self._threadlocal = threading.local()
        self.metadata = metadata
        self.url = url

    @property
    def instance(self):
        try:
            return self._threadlocal.instance
        except AttributeError:
            self._threadlocal.instance = neo4j.GraphDatabaseService(self.url)
            return self._threadlocal.instance
            
    @property
    def typemap(self):
        try:
            return self._typemap
        except AttributeError:
            from node import Node
            from relationship import Relationship
            self._typemap = {
                neo4j.Node: Node,
                #neo4j.Relationship: Relationship,
                neo4j.Path: self.mappath,
                list: self.maplist
            }
            return self._typemap
        
    def mappath(self, path):
        from node import Node
        #from relationship import Relationship
        out = []
        for i, edge in enumerate(path._edges):
            out.append(Node(path._nodes[i]))
            #out.append(Relationship(edge))
            out.append(edge)
        out.append(Node(path._nodes[-1]))
        return out

    def maplist(self, list):
        return [self.typemap[type(e)](e) for e in list]

    def cypher(self, *args, **kwargs):
        automap = kwargs.pop('automap', True)
        if automap:
            results = []
            qres = cypher.execute(self.instance, *args, **kwargs)[0]

            for row in qres:
                items = []
                for item in row:
                    try:
                        items.append(self.typemap[type(item)](item))
                    except KeyError:
                        items.append(item)
                results.append(items)

            from relationship import Relationship

            def _2nd_pass_map(lst):
                for idx, item in enumerate(lst):
                    if isinstance(item, neo4j.Relationship):
                        lst[idx] = Relationship(item)
                    elif isinstance(item, list):
                        _2nd_pass_map(item)
                return lst

            _2nd_pass_map(results)

            return results
        else:
            return cypher.execute(self.instance, *args, **kwargs)[0]

    def batch(self):
        return WriteBatch(self.instance)

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
