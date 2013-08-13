from exc import *
from metadata import metadata as m
from util import classproperty

class QueryFactory(object):

    @classproperty
    def base(cls):
        return BaseQuery()

    @classproperty
    def simple(cls):
        return SimpleQuery()

    @classmethod
    def node(cls, nodecls):
        q = cls.simple.start(c=nodecls.classnode.id)
        q = q.match('c<-[?:__extends__|__instance_of__*..]-i')
        q = q.where('()<-[:__instance_of__]-i')
        q = q.ret('i')
        return q 

    @classmethod
    def create_unique(cls, pattern, params):
        pass

class BaseQuery(object):

    def __init__(self):
        self.string = ''
        self.params = {}

    def copy(self):
        copy = self.__class__()
        copy.string = self.string
        copy.params = self.params.copy()
        return copy

    @property
    def query(self):
        return self.string

    def execute(self):
        return m.cypher(self.query, params=self.params)

class SimpleQuery(BaseQuery):

    def __init__(self):
        super(SimpleQuery, self).__init__()
        self._ret = ''
        self._opts = ''

    def copy(self):
        copy = super(SimpleQuery, self).copy()
        copy._ret = self._ret
        copy._opts = self._opts
        return copy

    @property
    def query(self):
        return self.string + self._ret + self._opts

    def all(self):
        return [x[0] for x in self.execute()]

    def count(self):
        return m.cypher(self.string + 'return count(*)', params=self.params)[0][0]

    def first(self):
        # NOTE: should be optimized with a limit in the query
        try:
            return self.all()[0]
        except IndexError:
            return None

    def one(self):
        # NOTE: should be optimized with a limit + count in the query
        all = self.all()
        if len(all) == 1:
            return all[0]
        elif len(all) == 0:
            raise NoResultFound()
        else:
            raise MultipleResultsFound()

    def start(self, **kwargs):
        copy = self.copy()
        copy.string = 'start'

        for name, value in kwargs.iteritems():
            key = "{0}_id".format(name)
            id = value if isinstance(value, int) else value.id

            copy.string += ' {0}=node({{{1}}}),'.format(name, key)
            copy.params[key] = id

        copy.string = copy.string[:-1] + ' ' if copy.string[-1] == ',' else copy.string + ' '
        return copy

    def match(self, clause):
        copy = self.copy()
        copy.string += 'match {0} '.format(clause)
        return copy

    def where(self, clause):
        copy = self.copy()
        copy.string += 'where {0} '.format(clause)
        return copy

    def filter(self, *clauses):
        copy = self.copy()
        copy.string += 'and ' + ' and '.join(clauses) + ' '
        return copy

    def ret(self, *keys):
        copy = self.copy()
        copy._ret = 'return ' + ', '.join(keys)
        return copy

    def order_by(self, *values):
        copy = self.copy()
        copy._opts += ' order by ' + ', '.join(values)
        return copy

    def offset(self, value):
        copy = self.copy()
        copy._opts += ' skip ' + str(int(value))
        return copy

    def limit(self, value):
        copy = self.copy()
        copy._opts += ' limit ' + str(int(value))
        return copy
