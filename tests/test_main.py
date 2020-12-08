import pytest
from werkzeug.datastructures import ImmutableMultiDict

from main import app


@pytest.fixture
def test_client():
    app.config["TESTING"] = True
    return app.test_client()


def test_GET_index(test_client):
    response = test_client.get("/")
    assert response.status_code == 200
    assert b"Registration of equipment and books." in response.data
    assert b"Enter one of the following keywords" in response.data


def test_GET_search_with_correct_query(test_client):
    response = test_client.get("/search?query=kindle")
    assert b"Search results for kindle" in response.data


def test_GET_search_with_incorrect_query(test_client):
    response = test_client.get("/search?unexpected_query=kindle", follow_redirects=True)
    assert b"Registration of equipment and books." in response.data
    assert b"Enter any keywords." in response.data


def test_GET_search_with_not_inputted_query(test_client):
    response = test_client.get("/search?query=", follow_redirects=True)
    assert b"Registration of equipment and books." in response.data
    assert b"Enter any keywords." in response.data


def test_GET_search_direct_access(test_client):
    response = test_client.get("/search", follow_redirects=True)
    assert b"Registration of equipment and books." in response.data
    assert b"Enter any keywords." in response.data


def test_GET_registration_direct_access(test_client):
    response = test_client.get("/registration", follow_redirects=True)
    assert b"Registration of equipment and books." in response.data
    assert b"Enter any keywords." in response.data


def test_POST_registration_success(test_client):
    test_client.get("/search?query=サーカスTC")
    response = test_client.post("/registration", data={"asin": "B07B7HG86W"})
    assert "Registration for details of テンマクデザイン サーカスTC" in response.data.decode("UTF-8")


def test_POST_registration_failure(test_client):
    response = test_client.post("/registration", follow_redirects=True)
    assert b"Registration of equipment and books." in response.data
    assert b"Please try the procedure again from the beginning, sorry for the inconvenience." in response.data


def test_POST_registration_contributors(test_client):
    test_client.get("/search?query=DeepLearning")
    response = test_client.post("/registration", data={"asin": "4873117585"})
    assert "ゼロから作るDeep Learning ―Pythonで学ぶディープラーニングの理論と実装" in response.data.decode("UTF-8")
    assert "斎藤 康毅" in response.data.decode("UTF-8")


def test_POST_register_airtable_success(test_client):
    imd = ImmutableMultiDict(
        [
            ('image_url', 'https://m.media-amazon.com/images/I/210tcugW9ML.jpg'),
            ('title', 'テンマクデザイン サーカス TC DX'),
            ('url', 'https://www.amazon.co.jp/dp/B07XB5WX89?tag=bellonieslog-22&linkCode=osi&th=1&psc=1'),
            ('asin', 'B07XB5WX89'),
            ('manufacturer', 'テンマクデザイン'),
            ('contributors', None),
            ('publication_date', None),
            ('product_group', 'Sports'),
            ('registrants_name', 'yusuke-sforzando'),
            ('default_positions', 'sforzando-kawasaki'),
            ('current_positions', 'sforzando-kawasaki'),
            ('note', ''),
            ('features', "['サーカスTC DX\\u3000サンドカラー', '【サーカスTCと共通 ●設営が簡単に出来るセットアップガイド付。']")
        ]
    )
    test_client.get("/search?query=サーカスTC")
    test_client.post("/registration", data={"asin": "B07XB5WX89"})
    response = test_client.post("/register_airtable", data=imd, follow_redirects=True)
    assert b"Registration completed!" in response.data


def test_POST_register_airtable_failure(test_client):
    test_client.get("/search?query=サーカスTC")
    test_client.post("/registration", data={"asin": "B07XB5WX89"})
    response = test_client.post("/register_airtable", data={}, follow_redirects=True)
    assert b"Registration failed." in response.data
