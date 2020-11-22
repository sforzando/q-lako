import pytest

from airtable_client import AirtableClient
from asset import Asset

registerable_asset = Asset(
    title="PlayStation 5 (CFI-1000A01)",
    asin="B08GGGBKRQ",
    url="https://www.amazon.co.jp/ソニー・インタラクティブエンタテインメント-PlayStation-5-CFI-1000A01/dp/B08GGGBKRQ/",
    images=[{"url": "https://images-na.ssl-images-amazon.com/images/I/61YYOeZy9aL.AC_SL1500.jpg"}],
    manufacture="ソニー・インタラクティブエンタテインメント",
    contributor="",
    product_group="Video game",
    publication_date="2020-11-14 02:01:01.847113+09:00",
    features="圧巻のスピード:統合I/O(Integrated I/O)により、カスタムされたCPU・GPU・SSDがその力を発揮。",
    default_position="sforzando 川崎",
    current_position="渡邉宅",
    note="リモートゲーム大会用に購入。",
    registrant_name="yusuke-sforzando")


@pytest.fixture
def airtable_client():
    airtable_client = AirtableClient()
    return airtable_client


def test_register(airtable_client):
    """Testing whether a dictionary with the proper field names can be registered correctly."""

    assert airtable_client.register_asset(registerable_asset)


def test_register_non_existent_key(airtable_client):
    """Testing an instance of the Airtable date class is an argument."""

    with pytest.raises(TypeError):
        airtable_client.register_asset({"test": "test"})
