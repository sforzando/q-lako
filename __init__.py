import os
from configparser import ConfigParser

from amazon.paapi import AmazonAPI
from dotenv import load_dotenv
from flask import Flask

from flash_message import FlashMessage

load_dotenv(verbose=True)
config_parser = ConfigParser()
config_parser.read("settings.ini", encoding="utf8")

app = Flask(__name__)
app.secret_key = os.urandom(16)
app.config["THEME_COLOR_GRAY"] = config_parser.get("THEME-COLOR", "theme_color_gray")
app.config["AIRTABLE_TABLE_NAME"] = config_parser.get("AIRTABLE", "airtable_table_name")

amazon_api_client = AmazonAPI(os.getenv("amazon_access_key"),
                              os.getenv("amazon_secret_key"),
                              os.getenv("amazon_partner_tag"),
                              "JP")

flash_message = FlashMessage()

if os.getenv("GAE_ENV", "").startswith("standard"):
    """ Production in GAE """

    app.config["IS_LOCAL"] = False
    import google.cloud.logging
    import logging

    client = google.cloud.logging.Client()
    handler = client.get_default_handler()
    cloud_logger = logging.getLogger(__name__)
    cloud_logger.setLevel(logging.DEBUG)
    cloud_logger.addHandler(handler)
else:
    """ Local execution """

    app.config["IS_LOCAL"] = True
    app.debug = True

    try:
        import flask_monitoringdashboard as dashboard

        dashboard.bind(app)
    except ImportError as ie:
        app.logger.warning(f"{ie}")
