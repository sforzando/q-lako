# !/usr/bin/env python3

import requests
from amazon.exception import AmazonException
from flask import request, render_template, url_for, session

from __init__ import app, amazon_api_client, airtable_client
from asset import Asset
from flash_message import FlashMessage, FlashCategories


@app.route("/", methods=["GET"])
def index():
    app.logger.info("index(): GET /")
    return render_template("index.html")


@app.route("/search", methods=["GET"])
def search():
    app.logger.info(f"search(): GET {request.full_path}")
    session["keyword"] = request.args.get('query', None)

    if not session["keyword"]:
        return FlashMessage.show_with_redirect("Enter any keywords.", FlashCategories.WARNING, url_for("index"))

    context_dict = {
        "subtitle": f"Search results for {session['keyword']}",
        "keyword": session["keyword"]
    }
    try:
        product_list = amazon_api_client.search_products(keywords=session["keyword"], item_count=30)
        session["product_list"] = product_list
        return render_template("search.html", **context_dict)
    except AmazonException as ae:
        app.logger.error(ae)
        return FlashMessage.show_with_redirect(f"Error occurred. {ae}", FlashCategories.ERROR, url_for("index"))


@app.route("/registration", methods=["GET", "POST"])
def registration():
    context_dict = {}
    if request.method == "GET":
        app.logger.info(f"registration: GET {request.full_path}")
        if session.get("product", None):
            context_dict["subtitle"] = f"Registration for details of {session.get('product').title}"
            return render_template("registration.html", **context_dict)
        else:
            return FlashMessage.show_with_redirect("Enter any keywords.", FlashCategories.WARNING, url_for("index"))

    app.logger.info("registration: POST /registration")
    app.logger.debug(f"{request.form=}")
    asin = request.form.get("asin", "")

    if not asin or not session.get("product_list", None):
        return FlashMessage.show_with_redirect(
            "Either the ASIN code was not posted correctly or the session could not be held. Please try again.",
            FlashCategories.WARNING,
            url_for("index"))

    for product in session["product_list"]:
        if product.asin == asin:
            if product.info.contributors:
                product.info.contributors = ", ".join(
                    [contributor.name for contributor in product.info.contributors])
            if product.product.features:
                product.product.features = "\n".join(product.product.features)
            context_dict["subtitle"] = f"Registration for details of {product.title}"
            session["product"] = product
            if product.info.product_group:
                context_dict["similar_items"] = airtable_client.get_similar_items_by_keyword(
                    product.info.product_group, session.get("keyword", None))
                app.logger.debug(f"{context_dict['similar_items']=}")
            if context_dict["similar_items"]:
                return FlashMessage.show_with_render_template(
                    "Similar items are registered.", FlashCategories.INFO, "registration.html", **context_dict)
            return render_template("registration.html", **context_dict)
    else:
        return FlashMessage.show_with_redirect(
            "An unexpected error has been detected. Please try again.",
            FlashCategories.WARNING,
            url_for("index"))


@app.route("/register_airtable", methods=["POST"])
def register_airtable():
    app.logger.info("register_airtable(): POST /register_airtable")
    app.logger.debug(f"{request.form=}")
    posted_asset = request.form.to_dict() if request.form else {}

    if not posted_asset:
        return FlashMessage.show_with_redirect(
            "Registration failed. Please try the procedure again from the beginning, sorry for the inconvenience.",
            FlashCategories.WARNING,
            url_for("index"))
    else:
        registrable_asset = Asset(
            title=posted_asset.get("title", None),
            asin=posted_asset.get("asin", None),
            url=posted_asset.get("url", None),
            images=[{"url": posted_asset.get("image_url", None)}],
            manufacture=posted_asset.get("manufacturer", None),
            contributor=posted_asset.get("contributors", None),
            product_group=posted_asset.get("product_group", None),
            publication_date=posted_asset.get("publication_date", None),
            features=posted_asset.get("features", None),
            default_position=posted_asset.get("default_positions", None),
            current_position=posted_asset.get("current_positions", None),
            note=posted_asset.get("note", None),
            registrant_name=posted_asset.get("registrants_name", None))

    try:
        airtable_client.register_asset(registrable_asset)
        app.logger.info(f"Registration completed! {registrable_asset=}")
        return FlashMessage.show_with_redirect("Registration completed!", FlashCategories.INFO, url_for("index"))
    except requests.exceptions.HTTPError as he:
        app.logger.error(he)
        return FlashMessage.show_with_redirect(
            f"Registration failed. Please try the procedure again. Error message: {he}",
            FlashCategories.ERROR,
            url_for("registration"))
    except TypeError as te:
        app.logger.error(te)
        return FlashMessage.show_with_redirect(
            f"Registration failed. Please try the procedure again. Error message: {te}",
            FlashCategories.ERROR,
            url_for("registration"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888)
