# !/usr/bin/env python3

from amazon.exception import AmazonException
from flask import render_template, request

from __init__ import app, amazon_api_client


@app.route("/", methods=["GET"])
def index():
    app.logger.info("index(): GET /")
    template_filename = "index.html"
    context_dict = {
        "subtitle": template_filename,
        "message": f"This is {template_filename}."
    }
    return render_template(template_filename, **context_dict)


@app.route("/search", methods=["GET"])
def search():
    template_filename = "search.html"
    keyword = request.args.get("query", "")
    context_dict = {
        "subtitle": template_filename,
        "keyword": keyword
    }
    if keyword:
        app.logger.info(f"search(): GET /{request.full_path}")
        try:
            context_dict["product_list"] = amazon_api_client.search_products(keywords=keyword)

        except AmazonException as ae:
            app.logger.error(f"{ae}")
            raise ae
    else:
        context_dict["message"] = "TOPページに戻ってキーワードを入力してください"
    return render_template(template_filename, **context_dict)


@ app.route("/registration", methods=["GET", "POST"])
def registration():
    app.logger.info("search(): POST /registration")
    asin = request.form.get("asin", "")
    context_dict = {
        "subtitle": "registration details",
        "asin": asin
    }
    if not asin:
        context_dict["message"] = "TOPページに戻ってキーワードを入力してください"

    return render_template("registration.html", **context_dict)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888)
