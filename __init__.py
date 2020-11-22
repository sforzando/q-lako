import os

from amazon.paapi import AmazonAPI
from dotenv import load_dotenv
from flask import Flask

load_dotenv(verbose=True)

app = Flask(__name__)

amazon_api_client = AmazonAPI(os.getenv("amazon_access_key"),
                              os.getenv("amazon_secret_key"),
                              os.getenv("amazon_partner_tag"),
                              "JP")

if os.getenv("GAE_ENV", "").startswith("standard"):
    """ Production in GAE """

    app.config["IS_LOCAL"] = False
    import google.cloud.logging
    from google.cloud.logging.handlers import CloudLoggingHandler
    import logging

    client = google.cloud.logging.Client()
    handler = CloudLoggingHandler(client)
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

# Read theme color from css file
try:
    with app.open_resource("static/css/common.css", "r") as f:
        theme_color = [line[-9:-2] for line in f if "--theme-color-gray:" in line]
except FileNotFoundError as fe:
    app.logger.error(fe)

app.config["THEME_COLOR"] = theme_color[0] if theme_color else "#fafafa"
