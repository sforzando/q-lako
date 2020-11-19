# !/usr/bin/env python3

import os
import requests

from airtable import Airtable


class AirtableClient:
    def __init__(self):
        """Initialize AirtableClient."""

        self.airtable_client = Airtable(os.getenv("airtable_base_id"), "q-lako", os.getenv("airtable_api_key"))

    def register_table(self, airtable_dict: dict):
        """Register with Airtable.

        Register to Airtable,taking as an argument a dictionary
        with key names and elements corresponding to the Airtable table.

        Args:
            airtable_dict (dict): A dictionary with key names and elements corresponding to the Airtable table.

        Retruns:
            bool: Returns True if the registration is successful, False if failure.

        """

        try:
            self.airtable_client.insert(airtable_dict)
        except requests.exceptions.HTTPError:
            return False
        else:
            return True

    def fetch_asin_list(self):
        asset_list = self.airtable_client.get_all(fields="Asset code")
        return [asset["fields"]["Asset code"] for asset in asset_list]
