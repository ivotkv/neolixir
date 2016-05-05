import re
from exc import *
from metadata import metadata as m
from utils import classproperty

NEST_CHARS = {
    '\'': '\'',
    '"': '"',
    '[': ']',
    '(': ')',
    '{': '}'
}

LOWERCASE_RE = re.compile(r'^(return|union)$', flags=re.I)

def tokenize(string):
    tokens = []
    idx = 0
    token = ''
    context = []
    while idx < len(string):
        if string[idx] == '\\':
            token += string[idx] + string[idx + 1]
            idx += 2
        elif len(context) == 0:
            if string[idx].isspace():
                if len(token) > 0:
                    if LOWERCASE_RE.match(token):
                        token = token.lower()
                    tokens.append(token)
                    token = ''
            else:
                if string[idx] in NEST_CHARS:
                    context.append(string[idx])
                token += string[idx]
            idx += 1
        else:
            if string[idx] == NEST_CHARS[context[-1]]:
                context.pop()
            elif string[idx] in NEST_CHARS:
                context.append(string[idx])
            token += string[idx]
            idx += 1
    if len(token) > 0:
        if LOWERCASE_RE.match(token):
            token = token.lower()
        tokens.append(token)
    return tokens

class Query(object):

    def __init__(self, string='', params=None):
        self.tokens = tokenize(string) if string else []
        self.params = params or {}

    @property
    def string(self):
        return ' '.join(self.tokens)

    def copy(self):
        copy = self.__class__()
        copy.tokens = [x for x in self.tokens]
        copy.params = self.params.copy()
        return copy

    def __copy__(self):
        return self.copy()

    def append(self, string, params=None):
        copy = self.copy()
        copy.tokens += tokenize(string)
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
