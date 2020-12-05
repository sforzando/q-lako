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
        "subtitle": f"Search results for {session.get('keyword', None)}",
        "keyword": session.get("keyword", None)
    }
    try:
        product_list = amazon_api_client.search_products(keywords=session.get("keyword", None))
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
                product.info.contributors = ", ".join(
                    [contributor.name for contributor in product.info.contributors])
            if product.product.features:
                print(f"{product.product.features=}")
                product.product.features = "\n".join(product.product.features)
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
    posted_asset = request.form.to_dict() if request.form else{}

    def convert_str_none_int_0(n: str) -> int:
        return 0 if n == "None" else n

    if posted_asset:
        registrable_asset = Asset(
            title=posted_asset.get("title", None),
            asin=posted_asset.get("asin", None),
            url=posted_asset.get("url", None),
            images=[{"url": posted_asset.get("image_url", None)}],
            manufacture=posted_asset.get("manufacturer", None),
            contributor=posted_asset.get("contributors", None),
            product_group=posted_asset.get("product_group", None),
            publication_date=convert_str_none_int_0(posted_asset.get("publication_date")),
            features=posted_asset.get("features", None),
            default_position=posted_asset.get("default_positions", None),
            current_position=posted_asset.get("current_positions", None),
            note=posted_asset.get("note", None),
            registrant_name=posted_asset.get("registrants_name", None))
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
