import sys
import traceback
from Queue import Queue
from threading import Thread

def same_type_and_value(x, y):
    return type(x) is type(y) and x == y

def checked_thread(func):

    def wrapper(*args, **kwargs):
    
        def run(q, *args, **kwargs):
            try:
                q.put(func(*args, **kwargs))
            except:
                q.put(sys.exc_info())

        q = Queue()
        t = Thread(target=run, args=(q,) + args, kwargs=kwargs)
        t.start()
        t.join()

        assert not q.empty(), 'unexpected empty queue in checked_thread()'
        value = q.get()
        assert not (isinstance(value, tuple) and 
                    isinstance(value[0], type) and
                    issubclass(value[0], Exception)), \
               ''.join(traceback.format_exception(*value))
        return value

    return wrapper
