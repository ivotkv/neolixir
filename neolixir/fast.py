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

from dummy import DummyNode, DummyRelationship

def fast_cypher(metadata, query, params=None):

    payload = {"query": query, "params": params or {}}
    response = metadata.graph.cypher.resource.post(payload).content

    return [hydrate(row) for row in response['data']]

def hydrate(data, seen=None):
    if seen is None:
        seen = {
            'nodes': {},
            'rels': {}
        }
    if isinstance(data, list):
        return [hydrate(item, seen=seen) for item in data]
    elif isinstance(data, dict) and 'self' in data:
        if data['self'].find('/db/data/node/') >= 0:
            id = int(data['metadata']['id'])
            try:
                node = seen['nodes'][id]
            except KeyError:
                node = DummyNode(id, data.get('data'))
                seen['nodes'][id] = node
            else:
                if data.has_key('data'):
                    node.properties.update(data['data'])
            return node
        elif data['self'].find('/db/data/relationship/') >= 0:
            id = data['metadata']['id']
            try:
                rel = seen['rels'][id]
            except KeyError:
                start_id = int(data['start'].split('/')[-1])
                try:
                    start = seen['nodes'][start_id]
                except KeyError:
                    start = DummyNode(start_id)
                    seen['nodes'][start_id] = start
                type = data['type']
                end_id = int(data['end'].split('/')[-1])
                try:
                    end = seen['nodes'][end_id]
                except KeyError:
                    end = DummyNode(end_id)
                    seen['nodes'][end_id] = end
                rel = DummyRelationship(id, start, type, end, data.get('data'))
                seen['rels'][id] = rel
            else:
                if data.has_key('data'):
                    rel.properties.update(data['data'])
            return rel
        else:
            return data
    else:
        return data
