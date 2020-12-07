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

    def fetch_table(self):
        """Fetch Airtable item list.

        Fetch the items stored in Airtable.

        Returns:
            A list of items with any field name stored in Airtable.
        """

        try:
            return self.airtable_client.get_all(view=app.config["AIRTABLE_VIEW_NAME"],
                                                fields=app.config["FETCH_FIELD_NAME"])
        except requests.exceptions.HTTPError as he:
            app.logger.error(he)
            raise he
