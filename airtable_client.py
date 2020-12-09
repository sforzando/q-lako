import os
from dataclasses import asdict
from fuzzysearch import find_near_matches

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

    def get_similar_items(self, keyword: str):
        """Fetch Airtable item list.

        Fetch the items stored in Airtable.

        Returns:
            similar_items (list): A list containing a dictionary of similar items.
        """

        similar_items = []
        try:
            item_list = [item for item in self.airtable_client.get_all(view=app.config["AIRTABLE_VIEW_NAME"],
                                                                       fields=app.config["FETCH_FIELD_NAME"])]
            for item in item_list:
                if find_near_matches(keyword, item["fields"]["title"], max_l_dist=1):
                    similar_items.append(item["fields"])
            return similar_items
        except requests.exceptions.HTTPError as he:
            app.logger.error(he)
            raise he
