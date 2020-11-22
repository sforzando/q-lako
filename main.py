# !/usr/bin/env python3

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
    products_list = []
    keyword = request.args.get("query", "")
    app.logger.info("search(): GET /search?query={}".format(keyword))
    products_list = amazon_api_client.search_products(keywords=keyword)
    context_dict = {
        "subtitle": template_filename,
        "keyword": keyword,
        "products_list": products_list
    }
    return render_template(template_filename, **context_dict)


@ app.route("/registration", methods=["GET", "POST"])
def registration():
    app.logger.info("search(): POST /registration")
    template_filename = "registration.html"
    context_dict = {
        "subtitle": template_filename,
        "asin": request.form["asin"]
    }
    return render_template(template_filename, **context_dict)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888)
