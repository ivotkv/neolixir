import re
from exc import *
from metadata import metadata as m
from utils import classproperty

class BaseQuery(object):

    def __init__(self, string='', params=None):
        self.string = string or ''
        self.params = params or {}

    def copy(self):
        return self.__class__(string=self.string, params=self.params.copy())

    def __copy__(self):
        return self.copy()

    def execute(self, string=None, automap=True, fast=False):
        return m.cypher(string or self.string, params=self.params, automap=automap, fast=fast)

class Query(BaseQuery):

    @property
    def string(self):
        return '\n'.join([self._clauses, self._return, self._order, self._skip, self._limit]).strip()

    @string.setter
    def string(self, string):
        self._clauses = ''
        self._return = ''
        self._order = ''
        self._skip = ''
        self._limit = ''
        self._append(string)

    def _set(self, string):
        if re.search(re.compile(r'\breturn\b', flags=re.I), string):
            self._order = ''
            self._return = 'return ' + re.split(re.compile(r'\breturn\b', flags=re.I), string)[1].strip()
            self._return = re.split(re.compile(r'\b(order|skip|limit)\b', flags=re.I), self._return)[0].strip()

        if re.search(re.compile(r'\border\b', flags=re.I), string):
            self._order = 'order ' + re.split(re.compile(r'\border\b', flags=re.I), string)[1].strip()
            self._order = re.split(re.compile(r'\b(skip|limit)\b', flags=re.I), self._order)[0].strip()

        if re.search(re.compile(r'\bskip\b', flags=re.I), string):
            self._skip = 'skip ' + re.split(re.compile(r'\bskip\b', flags=re.I), string)[1].strip()
            self._skip = re.split(re.compile(r'\blimit\b', flags=re.I), self._skip)[0].strip()

        if re.search(re.compile(r'\blimit\b', flags=re.I), string):
            self._limit = 'limit ' + re.split(re.compile(r'\blimit\b', flags=re.I), string)[1].strip()

    def set(self, string):
        copy = self.copy()
        copy._set(string)
        return copy

    def _append(self, string, params=None, clear=True):
        if not re.match('^\s*(return|order|skip|limit).*', string, flags=re.I):
            if clear:
                self._clear()
            self._clauses += ' ' + re.split(re.compile(r'\b(return|order|skip|limit)\b', flags=re.I), string)[0].strip()
        self._set(string)
        if params is not None:
            self.params.update(params)

    def append(self, string, params=None, clear=True):
        copy = self.copy()
        copy._append(string, params=params, clear=clear)
        return copy

    def _clear(self, *parts):
        if len(parts) == 0:
            self._return = ''
            self._order = ''
            self._skip = ''
            self._limit = ''
        else:
            for part in parts:
                if part == 'return':
                    self._return = ''
                    self._order = ''
                    self._skip = ''
                    self._limit = ''
                elif part in ('order', 'skip', 'limit'):
                    setattr(self, '_' + part, '')

    def clear(self, *parts):
        copy = self.copy()
        copy._clear(*parts)
        return copy

    @classmethod
    def node(cls, nodecls):
        return cls(string="""
        match (instance:{0})
        return instance
        """.format(nodecls.clslabel))

    """
    WARNING: The methods below are very limited and provided for partial Elixir-like compatibility only
    """
    def start(self, **kwargs):
        copy = self.copy()
        nodes = []

        for name, value in kwargs.iteritems():
            key = "{0}_id".format(name)
            id = value if isinstance(value, int) else value.id

            nodes.append('{0}=node({{{1}}})'.format(name, key))
            copy.params[key] = id

        copy.string = 'start ' + ', '.join(nodes)
        return copy

    def match(self, *clauses):
        return self.append('match {0}'.format(', '.join(clauses)), clear=False)

    def where(self, *clauses):
        return self.append('where {0}'.format(' and '.join(clauses)), clear=False)

    def return_(self, *keys):
        return self.set('return ' + ', '.join(keys))

    def order_by(self, *values):
        return self.set('order by ' + ', '.join(values))

    def skip(self, value):
        return self.set('skip ' + str(int(value)))

    def offset(self, value):
        return self.skip(value)

    def limit(self, value):
        return self.set('limit ' + str(int(value)))

    def all(self, automap=True):
        return [x[0] for x in self.execute(automap=automap)]

    def count(self):
        return self.set('return count(*)').execute(automap=False)[0][0]

    def first(self, automap=True):
        try:
            return self.limit(1).execute(automap=automap)[0][0]
        except IndexError:
            return None

    def one(self, automap=True):
        results = self.limit(2).execute(automap=automap)
        if len(results) == 1:
            return results[0][0]
        elif len(results) == 0:
            raise QueryError('No results found for one()')
        else:
            raise QueryError('Multiple results found for one()')
