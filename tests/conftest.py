from configparser import ConfigParser
from hashlib import sha256

import pytest

from main import app

config_parser = ConfigParser()
config_parser.read("settings_for_test.ini", encoding="utf8")


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(
            self, user_id=config_parser.get("ACCOUNT", "user_id"), password=config_parser.get("ACCOUNT", "password")):
        return self._client.post(
            "/login", data={"user_id": user_id, "password": password}, follow_redirects=True
        )

    def logout(self):
        return self._client.get("/logout", follow_redirects=True)


@pytest.fixture(scope='session')
def test_client():
    app.config["TESTING"] = True
    app.config["ACCOUNTS"] = ((config_parser.get("ACCOUNT", "user_id"),
                               sha256(config_parser.get("ACCOUNT", "password").encode("UTF-8")).hexdigest()),)
    app.config["AMAZON_ITEM_COUNT"] = int(config_parser.get("AMAZON_API", "item_count"))
    return app.test_client()


@pytest.fixture(scope='session')
def auth(test_client):
    return AuthActions(test_client)


@pytest.fixture(scope='session')
def authenticated_client(test_client, auth):
    auth.login()
    return test_client


@pytest.fixture(scope='session')
def flask_app_context():
    app.config["TESTING"] = True
    return app.app_context()
