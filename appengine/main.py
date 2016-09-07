# -*- coding: utf-8 -*-

import json
import logging
import flask
from google.appengine.api import taskqueue


logger = logging.getLogger(__name__)

app = flask.Flask(__name__)
app.config.update(
    DEBUG=False,
    JSON_AS_ASCII=False,
)


@app.route("/", methods=["GET", "POST"])
def main_page():
    return "num of pull queues: {}".format(count_pull_queues())


@app.route("/add-pull-queues", methods=["POST"])
def add_pull_queues():
    queues = flask.request.get_json()["queues"]
    tasks = [taskqueue.Task(payload=json.dumps(i), method="PULL") for i in queues]
    q = taskqueue.Queue('pull-queue')
    q.add(tasks)
    return "ok"


def count_pull_queues():
    q = taskqueue.Queue('pull-queue')
    n_queues = len(q.lease_tasks(lease_seconds=0, max_tasks=1000))
    logger.info("the numbers of pull queues: {}".format(n_queues))
    return n_queues
