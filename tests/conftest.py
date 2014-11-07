import os
import pytest
import warnings

warnings.simplefilter("error")

@pytest.fixture(scope='session')
def metadata():
    from neolixir import metadata
    if 'NEO4J_TEST_SERVER' in os.environ:
        metadata.url = 'http://{0}/db/data/'.format(os.environ['NEO4J_TEST_SERVER'])
    metadata.graph.delete_all()
    import models
    metadata.init()
    return metadata

@pytest.fixture()
def m(metadata):
    metadata.session.clear()
    return metadata
