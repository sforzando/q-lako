import pytest

from airtable_client import AirtableClient

airtable_dictionary = {
    "Name": "PlayStation 5 (CFI-1000A01)",
    "Asset code": "B08GGGBKRQ",
    "URL": "https://www.amazon.co.jp/ソニー・インタラクティブエンタテインメント-PlayStation-5-CFI-1000A01/dp/B08GGGBKRQ/",
    "Images":
        [
            {
                "url": "https://images-na.ssl-images-amazon.com/images/I/61YYOeZy9aL._AC_SL1500_.jpg"
            }
        ],
    "Maker": "ソニー・インタラクティブエンタテインメント",
    "Category": "Video game",
    "Released date": "2020-10-31",
    "Description": "圧巻のスピード:統合I/O(Integrated I/O)により、カスタムされたCPU・GPU・SSDがその力を発揮。",
        "Default position": "渡邉宅",
        "Current position": "渡邉宅",
        "note": "PS5",
        "Registrant name": "Yusuke",
        "Registered at": "2020-11-18"
}


@pytest.fixture
def airtable_client():
    airtable_client = AirtableClient()
    return airtable_client


def test_register(airtable_client):
    """Testing whether a dictionary with the proper field names can be registered correctly."""

    assert airtable_client.register_table(airtable_dictionary)


def test_register_illegal(airtable_client):
    """Testing when a non-existent field name is registered."""

    assert not airtable_client.register_table({"test": "test"})
