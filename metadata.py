from engine import Engine

class MetaData(object):

    def __init__(self):
        self._engine = Engine()

    @property
    def engine(self):
        return self._engine.instance
