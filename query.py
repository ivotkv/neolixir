from exc import *
from metadata import metadata as m

class Query(object):

    def __init__(self):
        self.params = {}
        self.string = ''
        self._ret = ''
        self._opt = ''

    def start(self, **kwargs):
        self.string = 'start'

        for name, value in kwargs.iteritems():
            key = "{0}_id".format(name)
            id = value if isinstance(value, int) else value.id

            self.string += ' {0}=node({{{1}}}),'.format(name, key)
            self.params[key] = id

        self.string = self.string[:-1] + ' ' if self.string[-1] == ',' else self.string + ' '
        return self

    def match(self, clause):
        self.string += 'match {0} '.format(clause)
        return self

    def where(self, clause):
        self.string += 'where {0} '.format(clause)
        return self

    def filter(self, *clauses):
        self.string += 'and ' + ' and '.join(clauses) + ' '
        return self

    def ret(self, *keys):
        self._ret = 'return ' + ', '.join(keys)
        return self

    def order_by(self, *values):
        self._opt += ' order by ' + ', '.join(values)
        return self

    def offset(self, value):
        self._opt += ' skip ' + str(int(value))
        return self

    def limit(self, value):
        self._opt += ' limit ' + str(int(value))
        return self

    def count(self):
        return m.cypher(self.string + 'return count(*)', params=self.params)[0][0]

    def all(self):
        return [x[0] for x in m.cypher(self.string + self._ret + self._opt, params=self.params)]

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
