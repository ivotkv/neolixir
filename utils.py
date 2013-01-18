import threading

class ThreadLocalRegistry(object):

    def __init__(self, *args, **kwargs):
        self.__args__ = args
        self.__creators__ = kwargs
        self.__registry__ = threading.local()

    def __getattr__(self, name):
        try:
            return getattr(self.__registry__, name)
        except AttributeError:
            func = self.__creators__.get(name, None)
            if func:
                value = func(*self.__args__)
                setattr(self.__registry__, name, value)
                return value
            else:
                raise AttributeError("Registry has no creator for: '{0}'".format(name))

    def __setattr__(self, name, value):
        if name[0] == '_':
            object.__setattr__(self, name, value)
        else:
            setattr(self.__registry__, name, value)
