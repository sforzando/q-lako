import pytest

from main import app


@pytest.fixture(scope='session')
def test_client():
    app.config["TESTING"] = True
    return app.test_client()


@pytest.fixture(scope='session')
def flask_app_context():
    app.config["TESTING"] = True
    return app.app_context()
