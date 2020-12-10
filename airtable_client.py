import os
from dataclasses import asdict

import requests

from airtable import Airtable

from __init__ import app
from asset import Asset


class AirtableClient:

    def __init__(self):
        """Initialize AirtableClient."""

        self.airtable_client = Airtable(os.getenv("airtable_base_id"),
                                        app.config["AIRTABLE_TABLE_NAME"], os.getenv("airtable_api_key"))

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
            app.logger.error(he)
            raise he
        except TypeError as te:
            app.logger.error(te)
            raise te

    def get_similar_items_by_titles(self, keywords: str):
        """Fetch Airtable item list.

        Fetch the items stored in Airtable.

        Returns:
            similar_items (list): A list containing a dictionary of similar items.
        """

        try:
            search_formula = f"Find('{keywords}',title)=1"
            return [Asset(
                title=similar_item["fields"]["title"],
                asin=similar_item["fields"]["asin"],
                url=similar_item["fields"].get("url", ""),
                images=similar_item["fields"].get("images", ""),
                manufacture=similar_item["fields"].get("manufacture", ""),
                contributor=similar_item["fields"].get("contributor", ""),
                product_group=similar_item["fields"].get("product_group", ""),
                publication_date=similar_item["fields"].get("publication_date", ""),
                features=similar_item["fields"].get("features", ""),
                default_position=similar_item["fields"].get("default_positions", ""),
                current_position=similar_item["fields"].get("current_positions", ""),
                note=similar_item["fields"].get("note", ""),
                registrant_name=similar_item["fields"].get("registrant_name", ""),
                registered_at=similar_item["fields"].get("registered_at", "")
            ) for similar_item in self.airtable_client.get_all(formula=search_formula)]

        except requests.exceptions.HTTPError as he:
            app.logger.error(he)
            raise he


if __name__ == "__main__":
    air = AirtableClient().get_similar_items_by_titles("Python")
    print(air)
