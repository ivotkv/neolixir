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
            id = data['metadata']['id']
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
                start_id = data['start'].split('/')[-1]
                try:
                    start = seen['nodes'][start_id]
                except KeyError:
                    start = DummyNode(start_id)
                    seen['nodes'][start_id] = start
                type = data['type']
                end_id = data['end'].split('/')[-1]
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
