from time import time
from collections import Iterable
from metadata import metadata as m

__all__ = ['observe']

class Event(object):

    def __init__(self, caller, event, target, *args):
        self.time = time()
        self.caller = caller
        self.event = event
        self.target = target
        self.args = args

    def __cmp__(self, other):
        return cmp((self.time, id(self)), (getattr(other, 'time', None), id(other)))

    def fire(self, suffix=None):
        event = '{0}_{1}'.format(self.event, suffix) if suffix else self.event
        self.caller.fire_event(event, self.target, *self.args)

class SessionEvents(dict):

    def add(self, caller, event, target, *args):
        key = (caller, event, target)
        if key in self:
            if event == 'change':
                args = (self[key].args[0], args[1])
        self[key] = Event(caller, event, target, *args)

    def fire_committed(self):
        for event in sorted(self.itervalues()):
            event.fire('committed')
        self.clear()

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

    def has_observer(self, event):
        return event in self._observers or event + '_committed' in self._observers

    def fire_event(self, event, target, *args):
        if hasattr(self, '_observers'):
            for observer in self._observers[event]:
                observer(self, event, target, *args)
            if event.find('_committed') < 0 and event + '_committed' in self._observers:
                m.session.events.add(self, event, target, *args)

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
