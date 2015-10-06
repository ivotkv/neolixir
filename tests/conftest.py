import os
import pytest
import warnings

warnings.simplefilter("error")

@pytest.fixture(scope='session')
def metadata():
    from py2neo.error import GraphError
    from neolixir import metadata
    if 'NEO4J_TEST_SERVER' in os.environ:
        metadata.url = 'http://{0}/db/data/'.format(os.environ['NEO4J_TEST_SERVER'])
    try:
        from py2neo import Unauthorized
        try:
            metadata.version
        except Unauthorized:
            metadata.authenticate('neo4j', 'neo4j')
    except ImportError:
        pass
    try:
        metadata.graph.delete_all()
    except GraphError as e:
        if str(e).find('response 403') > 0:
            metadata.change_password('neo4j', 'neo4j', 'testpass')
            metadata.change_password('neo4j', 'testpass', 'neo4j')
            metadata.graph.delete_all()
        else:
            raise e
    import models
    metadata.init()
    return metadata

@pytest.fixture()
def m(metadata):
    metadata.session.clear()
    return metadata
