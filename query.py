from exc import *
from metadata import metadata as m

class Query(object):

    def __init__(self):
        self.q = ''
        self.r = ''

    def start(self, **kwargs):
        self.q = 'start'
        for k, v in kwargs.iteritems():
            id = v if isinstance(v, int) else v.id
            self.q += ' {0}=node({1}),'.format(k, id)
        self.q = self.q[:-1] + ' ' if self.q[-1] == ',' else self.q + ' '
        return self

    def match(self, clause):
        self.q += 'match {0} '.format(clause)
        return self

    def where(self, clause):
        self.q += 'where {0} '.format(clause)
        return self

    def filter(self, *clauses):
        self.q += 'and ' + ' and '.join(clauses) + ' '
        return self

    def ret(self, *keys):
        self.r = 'return ' + ', '.join(keys)
        return self

    def all(self):
        return m.cypher(self.q + self.r)

    def first(self):
        all = self.all()
        if len(all) > 0:
            return all[0]
        else:
            raise NoResultFound()

    def one(self):
        all = self.all()
        if len(all) == 1:
            return all[0]
        elif len(all) == 0:
            raise NoResultFound()
        else:
            raise MultipleResultsFound()
