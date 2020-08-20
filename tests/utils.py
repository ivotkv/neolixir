# -*- coding: utf-8 -*-
# 
# The MIT License (MIT)
# 
# Copyright (c) 2013 Ivo Tzvetkov
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 

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
