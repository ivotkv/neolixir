import threading

class Session(object):

    def __init__(self, metadata=None):
        self._threadlocal = threading.local()
        self._metadata = metadata
