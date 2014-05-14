import pytest

@pytest.fixture(scope='session')
def metadata():
    from neolixir import metadata
    metadata.engine.clear()
    import models
    metadata.init()
    return metadata

@pytest.fixture()
def m(metadata):
    metadata.session.clear()
    return metadata
