# !/usr/bin/env python3

from hashlib import sha256

import requests
from amazon.exception import AmazonException
from flask import redirect, request, render_template, url_for, session
from flask_login import login_required, login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired

from __init__ import app, amazon_api_client
from airtable_client import AirtableClient
from asset import Asset
from flash_message import FlashMessage, FlashCategories
from user import User


class LoginForm(FlaskForm):
    user_id = StringField('user_id', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    login_form = LoginForm()
    if request.method == "GET":
        app.logger.info("login(): GET /login")
        return render_template("login.html", login_form=login_form)
    else:
        app.logger.info("login(): POST /login")
        if login_form.validate_on_submit():
            user_id = login_form.user_id.data
            password = sha256(login_form.password.data.encode("UTF-8")).hexdigest()
            if (user_id, password) in app.config["ACCOUNTS"]:
                app.logger.info(f"{user_id} is logged in.")
                login_user(User(user_id))
                return redirect(url_for("index"))
            else:
                return FlashMessage.show_with_redirect(
                    "The user_id or password is incorrect.", FlashCategories.ERROR, url_for("login"))
        else:
            return FlashMessage.show_with_redirect("Log in failed.", FlashCategories.ERROR, url_for("login"))


@app.route("/logout", methods=["GET"])
def logout():
    app.logger.info("logout(): GET /logout")
    logout_user()
    return FlashMessage.show_with_redirect("Log out successfully.", FlashCategories.INFO, url_for("login"))


@app.route("/", methods=["GET"])
@login_required
def index():
    app.logger.info("index(): GET /")
    return render_template("index.html")


@app.route("/search", methods=["GET"])
@login_required
def search():
    app.logger.info(f"search(): GET {request.full_path}")
    keyword = request.args.get("query", None)
    session.pop("_flashes", None)

    if not keyword:
        return FlashMessage.show_with_redirect("Enter any keywords.", FlashCategories.WARNING, url_for("index"))

    context_dict = {
        "subtitle": f"Search results for {keyword}",
        "keyword": keyword
    }
    try:
        product_list = amazon_api_client.search_products(keywords=keyword, item_count=30)
        session["product_list"] = product_list if product_list else []
        return render_template("search.html", **context_dict)
    except AmazonException as ae:
        app.logger.error(ae)
        return FlashMessage.show_with_redirect(f"Error occurred. {ae}", FlashCategories.ERROR, url_for("index"))


@app.route("/registration", methods=["GET", "POST"])
@login_required
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
            "Please try the procedure again from the beginning, sorry for the inconvenience.",
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

    if session.get("product", None):
        return render_template("registration.html", **context_dict)
    else:
        return FlashMessage.show_with_redirect(
            "Please try the procedure again from the beginning, sorry for the inconvenience.",
            FlashCategories.WARNING,
            url_for("index"))


@app.route("/register_airtable", methods=["POST"])
@login_required
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
        AirtableClient().register_asset(registrable_asset)
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
