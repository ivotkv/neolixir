import os
import pytest

@pytest.fixture(scope='session')
def metadata():
    from neolixir import metadata
    if 'NEO4J_TEST_SERVER' in os.environ:
        metadata.engine = 'http://{0}/db/data/'.format(os.environ['NEO4J_TEST_SERVER'])
    metadata.engine.clear()
    import models
    metadata.init()
    return metadata

@pytest.fixture()
def m(metadata):
    metadata.session.clear()
    return metadata
