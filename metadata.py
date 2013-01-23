from engine import Engine
from session import Session

class MetaData(object):

    def __init__(self, url='http://localhost:7474/db/data/'):
        self._engine = Engine(url=url, metadata=self)
        self._session = Session(metadata=self)
        self._entities = {}

    @property
    def engine(self):
        return self._engine.instance

    @property
    def execute(self):
        return self._engine.execute

    @property
    def session(self):
        return self._session

    @property
    def entities(self):
        return self._entities
