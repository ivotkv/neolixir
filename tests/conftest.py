import pytest
import neolixir.metadata
import models

@pytest.fixture(scope='session')
def metadata():
    neolixir.metadata.init(reset=True)
    return neolixir.metadata

@pytest.fixture()
def m(metadata):
    metadata.session.clear()
    return metadata
