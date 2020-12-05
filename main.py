# !/usr/bin/env python3

from amazon.exception import AmazonException
from flask import request, render_template, url_for, session

from __init__ import app, amazon_api_client
from asset import Asset
from airtable_client import AirtableClient
from flash_message import FlashMessage, FlashCategories


def clear_session():
    session.pop("keyword", None)
    session.pop("product_list", None)
    session.pop("product", None)


@app.route("/", methods=["GET"])
def index():
    app.logger.info("index(): GET /")
    clear_session()
    return render_template("index.html")


@app.route("/search", methods=["GET"])
def search():
    app.logger.info(f"search(): GET {request.full_path}")
    session["keyword"] = request.args.get('query', None)

    if not session.get("keyword", None):
        return FlashMessage.show_with_redirect("Enter any keywords.", FlashCategories.WARNING, url_for("index"))

    context_dict = {
        "subtitle": f"Search results for {session['keyword']}",
        "keyword": session["keyword"]
    }
    try:
        product_list = amazon_api_client.search_products(keywords=session["keyword"])
        session["product_list"] = product_list if product_list else []
        return render_template("search.html", **context_dict)
    except AmazonException as ae:
        app.logger.error(ae)
        return FlashMessage.show_with_redirect(f"Error occurred. {ae}", FlashCategories.ERROR, url_for("index"))


@ app.route("/registration", methods=["GET", "POST"])
def registration():
    if request.method == "GET":
        app.logger.info(f"registration: GET {request.full_path}")
        return FlashMessage.show_with_redirect("Enter any keywords.", FlashCategories.WARNING, url_for("index"))

    app.logger.info("registration: POST /registration")
    app.logger.debug(f"{request.form=}")
    asin = request.form.get("asin", "")

    if not asin or not session.get("product_list", None):
        return FlashMessage.show_with_redirect(
            "Please try the procedure again from the beginning, sorry for the inconvenience.",
            FlashCategories.WARNING,
            url_for("index"))

    context_dict = {}
    session.pop("product", None)
    for product in session["product_list"]:
        if product.asin == asin:
            if product.info.contributors:
                product.info.contributors = ",".join(
                    [contributor.name for contributor in product.info.contributors])
            if product.product.features:
                product.product.features = ",".join(product.product.features)
            context_dict["subtitle"] = f"Registration for details of {product.title}"
            session["product"] = product

    if session.get("product", None):
        return render_template("registration.html", **context_dict)
    else:
        return FlashMessage.show_with_redirect(
            "Please try the procedure again from the beginning, sorry for the inconvenience.",
            FlashCategories.WARNING,
            url_for("index"))


@app.route("/register_airtable", methods=["POST"])
def register_airtable():
    app.logger.info("register_airtable(): POST /register_airtable")
    app.logger.debug(f"{request.form=}")
    posted_asset = request.form.to_dict() if request.form else {}
    if posted_asset:
        registrable_asset = Asset(
            title=posted_asset["title"],
            asin=posted_asset["asin"],
            url=posted_asset["url"],
            images=[{"url": posted_asset["image_url"]}],
            manufacture=posted_asset["manufacturer"],
            contributor=posted_asset["contributors"],
            product_group=posted_asset["product_group"],
            publication_date=0 if posted_asset["publication_date"] else 0,
            features=posted_asset["features"],
            default_position=posted_asset["default_positions"],
            current_position=posted_asset["current_positions"],
            note=posted_asset["note"],
            registrant_name=posted_asset["registrants_name"])
        AirtableClient().register_asset(registrable_asset)
        app.logger.info(f"Registration completed! {registrable_asset=}")
        return FlashMessage.show_with_redirect("Registration completed!", FlashCategories.INFO, url_for("index"))
    else:
        context_dict = {
            "subtitle": posted_asset.get("title", None)
        }
        app.logger.debug(f"{context_dict}=")
        return FlashMessage.show_with_render_template("Registration failed.", FlashCategories.ERROR,
                                                      "registration.html", **context_dict)


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=8888)
