import os

import pytest
from flask import session
from werkzeug.datastructures import ImmutableMultiDict

from main import app


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username="account_for_test", password="password_for_test"):
        return self._client.post(
            "/login", data={"user_id": username, "password": password}, follow_redirects=True
        )

    def logout(self):
        return self._client.get("/logout", follow_redirects=True)


@pytest.fixture
def test_client():
    app.config["TESTING"] = True
    return app.test_client()


@pytest.fixture
def auth(test_client):
    return AuthActions(test_client)


@pytest.fixture
def authenticated_client(test_client, auth):
    auth.login()
    return test_client


def test_login_success(test_client, auth):
    assert test_client.get("/login").status_code == 200
    response = auth.login()
    assert b"Registration of equipment and books." in response.data


def test_login_failure_user_id_not_correct(test_client):
    response = test_client.post(
        "/login",
        data={
            "user_id": "dummy",
            "password": os.getenv("password")},
        follow_redirects=True)
    assert b"Log in failed." in response.data


def test_login_failure_password_not_correct(test_client):
    response = test_client.post(
        "/login",
        data={
            "user_id": os.getenv("user_id"),
            "password": "dummy"},
        follow_redirects=True)
    assert b"Log in failed." in response.data


def test_logout(test_client, auth):
    auth.login()

    with test_client:
        response = auth.logout()
        assert b"Log out successfully." in response.data
        assert "user_id" not in session


def test_GET_index(authenticated_client):
    response = authenticated_client.get("/")
    assert response.status_code == 200
    assert b"Registration of equipment and books." in response.data
    assert b"Enter one of the following keywords" in response.data


def test_GET_search_with_correct_query(authenticated_client):
    response = authenticated_client.get("/search?query=kindle")
    assert b"Search results for kindle" in response.data


def test_GET_search_with_incorrect_query(authenticated_client):
    response = authenticated_client.get("/search?unexpected_query=kindle", follow_redirects=True)
    assert b"Registration of equipment and books." in response.data
    assert b"Enter any keywords." in response.data


def test_GET_search_with_not_inputted_query(authenticated_client):
    response = authenticated_client.get("/search?query=", follow_redirects=True)
    assert b"Registration of equipment and books." in response.data
    assert b"Enter any keywords." in response.data


def test_GET_search_direct_access(authenticated_client):
    response = authenticated_client.get("/search", follow_redirects=True)
    assert b"Registration of equipment and books." in response.data
    assert b"Enter any keywords." in response.data


def test_GET_registration_direct_access(authenticated_client):
    response = authenticated_client.get("/registration", follow_redirects=True)
    assert b"Registration of equipment and books." in response.data
    assert b"Enter any keywords." in response.data


def test_POST_registration_success(authenticated_client):
    authenticated_client.get("/search?query=UNIX")
    response = authenticated_client.post("/registration", data={"asin": "4274064069"})
    assert "Registration for details of UNIXという考え方―その設計思想と哲学" in response.data.decode("UTF-8")


def test_POST_registration_failure(authenticated_client):
    response = authenticated_client.post("/registration", follow_redirects=True)
    assert b"Registration of equipment and books." in response.data
    assert b"Please try the procedure again from the beginning, sorry for the inconvenience." in response.data


def test_POST_registration_contributors(authenticated_client):
    authenticated_client.get("/search?query=DeepLearning")
    response = authenticated_client.post("/registration", data={"asin": "4873117585"})
    assert "ゼロから作るDeep Learning ―Pythonで学ぶディープラーニングの理論と実装" in response.data.decode("UTF-8")
    assert "斎藤 康毅" in response.data.decode("UTF-8")


def test_POST_register_airtable_success(authenticated_client):
    imd = ImmutableMultiDict(
        [
            ("image_url", "https://m.media-amazon.com/images/I/210tcugW9ML.jpg"),
            ("title", "テンマクデザイン サーカス TC DX"),
            ("url", "https://www.amazon.co.jp/dp/B07XB5WX89?tag=bellonieslog-22&linkCode=osi&th=1&psc=1"),
            ("asin", "B07XB5WX89"),
            ("manufacturer", "テンマクデザイン"),
            ("contributors", None),
            ("publication_date", None),
            ("product_group", "Sports"),
            ("registrants_name", "yusuke-sforzando"),
            ("default_positions", "sforzando-kawasaki"),
            ("current_positions", "sforzando-kawasaki"),
            ("note", ""),
            ("features", "['サーカスTC DX\\u3000サンドカラー', '【サーカスTCと共通 ●設営が簡単に出来るセットアップガイド付。']")
        ]
    )
    authenticated_client.get("/search?query=サーカスTC")
    authenticated_client.post("/registration", data={"asin": "B07XB5WX89"})
    response = authenticated_client.post("/register_airtable", data=imd, follow_redirects=True)
    assert b"Registration completed!" in response.data


def test_POST_register_airtable_failure(authenticated_client):
    authenticated_client.get("/search?query=サーカスTC")
    authenticated_client.post("/registration", data={"asin": "B07XB5WX89"})
    response = authenticated_client.post("/register_airtable", data={}, follow_redirects=True)
    assert b"Registration failed." in response.data
