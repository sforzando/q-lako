import os
import secrets
from configparser import ConfigParser

from amazon.paapi import AmazonAPI
from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from flask_session import Session

from user import User

load_dotenv(verbose=True)
config_parser = ConfigParser()
config_parser.read("settings.ini", encoding="utf8")

app = Flask(__name__)
app.secret_key = secrets.token_bytes(32)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = u"Please Log in."
login_manager.login_message_category = "info"

SESSION_TYPE = "filesystem"
SESSION_FILE_DIR = "/tmp"
app.config.from_object(__name__)
Session(app)

app.config["THEME_COLOR_GRAY"] = config_parser.get("THEME-COLOR", "theme_color_gray")
app.config["AIRTABLE_TABLE_NAME"] = config_parser.get("AIRTABLE", "airtable_table_name")
app.config["ASSET_POSITIONS"] = config_parser.get("ASSET-PROPERTY", "positions").split(',')
app.config["ASSET_REGISTRANTS"] = config_parser.get("ASSET-PROPERTY", "registrants").split(',')

amazon_api_client = AmazonAPI(os.getenv("amazon_access_key"),
                              os.getenv("amazon_secret_key"),
                              os.getenv("amazon_partner_tag"),
                              "JP")

app.config["ACCOUNTS"] = tuple(tuple(ID_PASS.split(":")) for ID_PASS in os.getenv("accounts", None).split(","))

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


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)
