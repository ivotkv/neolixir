import re
from exc import *
from metadata import metadata as m
from utils import classproperty

class Query(object):

    def __init__(self, string='', params=None):
        self.string = string or ''
        self.params = params or {}

    def copy(self):
        return self.__class__(string=self.string, params=self.params.copy())

    def __copy__(self):
        return self.copy()

    def append(self, string, params=None):
        copy = self.copy()
        copy.string += ' ' + string
        if params is not None:
            copy.params.update(params)
        return copy

    def execute(self, automap=True, fast=False):
        return m.cypher(self.string, params=self.params, automap=automap, fast=fast)

    @classmethod
    def node(cls, nodecls):
        return cls(string='match (instance:{0})'.format(nodecls.clslabel))

    """
    WARNING: The methods below are very limited and provided for partial Elixir-like compatibility only
    """
    def offset(self, value):
        ret = 'return instance' if not re.search(re.compile(r'\breturn\b', flags=re.I), self.string) else ''
        return self.append('{0} skip {1}'.format(ret, str(int(value))))

    def limit(self, value):
        ret = 'return instance' if not re.search(re.compile(r'\breturn\b', flags=re.I), self.string) else ''
        return self.append('{0} limit {1}'.format(ret, str(int(value))))

    def all(self, automap=True, fast=False):
        if not re.search(re.compile(r'\breturn\b', flags=re.I), self.string):
            return self.append('return instance').all(automap=automap, fast=fast)
        return [x[0] for x in self.execute(automap=automap, fast=fast)]

    def first(self, automap=True):
        if not re.search(re.compile(r'\breturn\b', flags=re.I), self.string):
            return self.append('return instance').first(automap=automap)
        try:
            return self.limit(1).execute(automap=automap)[0][0]
        except IndexError:
            return None

    def one(self, automap=True):
        if not re.search(re.compile(r'\breturn\b', flags=re.I), self.string):
            return self.append('return instance').one(automap=automap)
        results = self.limit(2).execute(automap=automap)
        if len(results) == 1:
            return results[0][0]
        elif len(results) == 0:
            raise QueryError('No results found for one()')
        else:
            raise QueryError('Multiple results found for one()')

    def count(self):
        return self.append('return count(*)').execute(automap=False, fast=True)[0][0]
