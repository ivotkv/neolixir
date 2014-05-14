import pytest
import neolixir
import models

@pytest.fixture(scope='session')
def metadata():
    neolixir.metadata.engine.clear()
    neolixir.metadata.init()
    return neolixir.metadata

@pytest.fixture()
def m(metadata):
    metadata.session.clear()
    return metadata
