from collections import Iterable

__all__ = ['observe']

class ObserverDict(dict):

    def copy(self):
        copy = ObserverDict()
        for key, value in self.iteritems():
            copy[key] = value.copy()
        return copy

    def __getitem__(self, key):
        try:
            return super(ObserverDict, self).__getitem__(key)
        except KeyError:
            self[key] = set()
            return super(ObserverDict, self).__getitem__(key)

class ObservableMeta(type):

    def __init__(cls, name, bases, dict_):
        super(ObservableMeta, cls).__init__(name, bases, dict_)

        # inherited observers
        cls._observers = cls._observers.copy() if hasattr(cls, '_observers') else ObserverDict()
        for base in bases:
            if hasattr(base, '_observers'):
                for event, observers in base._observers.iteritems():
                    for observer in observers:
                        cls._observers[event].add(observer)

class Observable(object):

    def add_observers(self, observer_dict):
        if not hasattr(self, '_observers'):
            self._observers = ObserverDict()
        elif hasattr(self.__class__, '_observers'):
            if self._observers is self.__class__._observers:
                self._observers = self._observers.copy()
        for event, observers in observer_dict.iteritems():
            if not isinstance(observers, Iterable):
                observers = [observers]
            for observer in observers:
                self._observers[event].add(observer)

    def fire_event(self, event, *args, **kwargs):
        if hasattr(self, '_observers'):
            for observer in self._observers[event]:
                observer(self, event, *args, **kwargs)

def observe(observer_dict):

    def decorate(obj):
        if not hasattr(obj, '_observers'):
            obj._observers = ObserverDict()
        for event, observers in observer_dict.iteritems():
            if not isinstance(observers, Iterable):
                observers = [observers]
            for observer in observers:
                obj._observers[event].add(observer)
        return obj

    return decorate
