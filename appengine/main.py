# -*- coding: utf-8 -*-

# Additional modules
import flask

app = flask.Flask(__name__)
app.config.update(
    DEBUG=False,
    JSON_AS_ASCII=False,
)


@app.route("/", methods=["GET"])
def main_page():
    return "Hell World!"
