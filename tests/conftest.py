import pytest

from app import create_app
from app import routes


@pytest.fixture()
def app():
    app = create_app("testing")
    # Reset the in-memory store between tests.
    routes._ITEMS.clear()
    routes._NEXT_ID = 1
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()
