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

    def delete_asset_by_title(self, value: str):
        """Delete Airtable asset.

        Deletes the equipment registered in the Airtable with the value of the title field as an argument.

        Args:
            value (str): The values corresponding to the title-field in Airtable.

        Returns:
            Airtable API response (dict): Dictionary of successful or unsuccessful deletions and IDs of items.
        """

        try:
            return self.airtable_client.delete_by_field("title", value)
        except KeyError as ke:
            app.logger.error(ke)
            raise ke
