# -*- coding: utf-8 -*-
# 
# The MIT License (MIT)
# 
# Copyright (c) 2013 Ivaylo Tzvetkov, ChallengeU
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 

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
NO_SUBNEST = {'\'', '"'}

RETURN_RE = re.compile(r'^return$', flags=re.I)
RETURN_OPTS_RE = re.compile(r'^(order|skip|limit)$', flags=re.I)
ORDER_RE = re.compile(r'^order$', flags=re.I)
SKIP_RE = re.compile(r'^skip$', flags=re.I)
LIMIT_RE = re.compile(r'^limit$', flags=re.I)
SKIP_OR_LIMIT_RE = re.compile(r'^(skip|limit)$', flags=re.I)
UNION_RE = re.compile(r'^union$', flags=re.I)

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
            elif context[-1] not in NO_SUBNEST and string[idx] in NEST_CHARS:
                context.append(string[idx])
            token += string[idx]
            idx += 1
    if len(token) > 0:
        tokens.append(token)
    if len(context) > 0:
        raise ValueError("unclosed nestings in query: {0}".format(' '.join(context)))
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
        new_tokens = tokenize(string)
        return_idx = None
        union_idx = None
        for idx, token in enumerate(copy.tokens):
            if RETURN_RE.match(token):
                return_idx = idx
            elif UNION_RE.match(token):
                union_idx = idx
        new_return_idx = None
        new_union_idx = None
        for idx, token in enumerate(new_tokens):
            if new_return_idx is None and RETURN_RE.match(token):
                new_return_idx = idx
            elif new_union_idx is None and UNION_RE.match(token):
                new_union_idx = idx
        if return_idx is not None and new_return_idx is None:
            if RETURN_OPTS_RE.match(new_tokens[0]):
                extra_tokens = copy.tokens[return_idx:]
                copy.tokens = copy.tokens[:return_idx]
                if ORDER_RE.match(new_tokens[0]):
                    regex = RETURN_OPTS_RE
                elif SKIP_RE.match(new_tokens[0]):
                    regex = SKIP_OR_LIMIT_RE
                else:
                    regex = LIMIT_RE
                while extra_tokens and not regex.match(extra_tokens[0]):
                    copy.tokens.append(extra_tokens.pop(0))
                copy.tokens += new_tokens
            else:
                copy.tokens = copy.tokens[:return_idx] + new_tokens + copy.tokens[return_idx:]
        elif return_idx is None or new_return_idx is None or \
             new_union_idx is not None and new_union_idx < new_return_idx:
            copy.tokens += new_tokens
        else:
            copy.tokens = copy.tokens[:return_idx] + new_tokens
        if params is not None:
            copy.params.update(params)
        return copy

    def execute(self, automap=True, fast=False):
        return m.cypher(self.string, params=self.params, automap=automap, fast=fast)

    @classmethod
    def node(cls, nodecls):
        return cls(string='match (instance:{0}) return instance'.format(nodecls.clslabel))

    """
    WARNING: The methods below are very limited and provided for partial Elixir-like compatibility only
    """
    def offset(self, value):
        return self.append('skip {0}'.format(str(int(value))))

    def limit(self, value):
        return self.append('limit {0}'.format(str(int(value))))

    def all(self, automap=True, fast=False):
        return [x[0] for x in self.execute(automap=automap, fast=fast)]

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

    def count(self):
        return self.append('return count(*)').execute(automap=False, fast=True)[0][0]
