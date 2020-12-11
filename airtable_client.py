import os
from dataclasses import asdict

import requests
from airtable import Airtable
from dateutil.parser import parse
from flask import current_app
from fuzzysearch import find_near_matches

from asset import Asset


class AirtableClient:

    def __init__(self):
        """Initialize AirtableClient."""

        self.airtable_client = Airtable(os.getenv("airtable_base_id"),
                                        current_app.config["AIRTABLE_TABLE_NAME"], os.getenv("airtable_api_key"))

    def register_asset(self, asset: Asset):
        """Register to Airtable.

        Register a dictionary with the appropriate key and value to Airtable.

        Args:
            asset (Asset): Asset dataclass with field name of Assets table on Airtable.

        Returns:
            Dictionary registered in Airtable.
        """

        try:
            return self.airtable_client.insert(asdict(asset))
        except requests.exceptions.HTTPError as he:
            current_app.logger.error(he)
            raise he
        except TypeError as te:
            current_app.logger.error(te)
            raise te

    def get_similar_items_by_keyword(self, product_group: str, keyword: str):
        """Fetch Airtable item list.

        It retrieves items with a common product group stored in the Airtable and
        outputs similar items related to the keyword.

        Args:
            keyword (str): Keywords used in the search.
            product_group (str): Product group name for the specified item.

        Returns:
            similar_items (list<Asset>): List of Asset classes for similar items.
        """

        try:
            product_group_list = self.airtable_client.search(
                field_name="product_group", field_value=product_group)
            similar_items = []
            for item in product_group_list:
                if find_near_matches(keyword, item["fields"]["title"], max_l_dist=1):
                    similar_items.append(item)

            return [Asset(
                title=similar_item["fields"]["title"],
                asin=similar_item["fields"]["asin"],
                url=similar_item["fields"].get("url", None),
                images=similar_item["fields"].get("images", None),
                manufacture=similar_item["fields"].get("manufacture", None),
                contributor=similar_item["fields"].get("contributor", None),
                product_group=similar_item["fields"].get("product_group", None),
                publication_date=similar_item["fields"].get("publication_date", None),
                features=similar_item["fields"].get("features", None),
                default_position=similar_item["fields"].get("default_positions", None),
                current_position=similar_item["fields"].get("current_positions", None),
                note=similar_item["fields"].get("note", None),
                registrant_name=similar_item["fields"].get("registrant_name", None),
                registered_at=parse(similar_item["fields"].get("registered_at", None)).strftime("%Y/%d/%m %H:%M")
            ) for similar_item in similar_items]
        except requests.exceptions.HTTPError as he:
            current_app.logger.error(he)
            raise he
