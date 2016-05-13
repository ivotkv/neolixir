# -*- coding: utf-8 -*-
# 
# The MIT License (MIT)
# 
# Copyright (c) 2013 Ivaylo Tzvetkov, ChallengeU
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 

import py2neo

if '2.0' <= py2neo.__version__ < '2.1':

    """
    This sets the default socket timeout to 300 seconds.
    """
    py2neo.packages.httpstream.http.socket_timeout = 300

    """
    This restores the id property for consistency with previous versions.
    """
    from py2neo import Node, Relationship
    Node.id = Node._id
    Relationship.id = Relationship._id

    """
    Replace py2neo's json with simplejson if available for performance improvement.
    """
    try:
        import simplejson
        from datetime import date, time, datetime
        from decimal import Decimal

        class JSONEncoder(simplejson.JSONEncoder):

            def default(self, obj):
                if isinstance(obj, (datetime, date, time)):
                    return obj.isoformat()
                if isinstance(obj, Decimal):
                    return str(obj)
                if isinstance(obj, (set, frozenset)):
                    return list(obj)
                if isinstance(obj, complex):
                    return [obj.real, obj.imag]
                return simplejson.JSONEncoder.default(self, obj)

        py2neo.packages.httpstream.http.json = simplejson
        py2neo.packages.httpstream.http.JSONEncoder = JSONEncoder

    except ImportError:
        pass

    """
    This adds consistent subclasses to GraphError for easier exception catching
    """
    from py2neo.error import GraphError

    def __new__(cls, *args, **kwargs):
        try:
            exception = kwargs["exception"]
            error_cls = cls.subcls(exception)
        except KeyError:
            error_cls = cls
        return Exception.__new__(error_cls, *args)

    def subcls(cls, name):
        try:
            return cls._subcls[name]
        except KeyError:
            try:
                cls._subcls[name] = type(name, (cls,), {})
            except TypeError:
                # for Python 2.x
                cls._subcls[name] = type(str(name), (cls,), {})
            return cls._subcls[name]

    GraphError._subcls = {}
    GraphError.subcls = classmethod(subcls)
    GraphError.__new__ = classmethod(__new__)

    """
    This ensures consistent cypher result format for batches (see __hydrate()).
    Redefined in full since the name-mangled __hydrate makes it difficult to override cleanly.
    """
    from py2neo.batch.core import JobResult, GraphError, BatchError, ustr, raise_from

    def hydrate(cls, data, batch):
        graph = getattr(batch, "graph", None)
        job_id = data["id"]
        uri = data["from"]
        status_code = data.get("status")
        location = data.get("location")
        if graph is None or batch[job_id].raw_result:
            body = data.get("body")
        else:
            body = None
            try:
                body = graph.hydrate(data.get("body"))
            except GraphError as error:
                message = "Batch job %s failed with %s\n%s" % (
                    job_id, error.__class__.__name__, ustr(error))
                raise_from(BatchError(message, batch, job_id, status_code, uri, location), error)
        return cls(batch, job_id, uri, status_code, location, body)

    JobResult.hydrate = classmethod(hydrate)

else:
    raise ImportError("Untested version of py2neo ({0}), please check overrides.".format(py2neo.__version__))
