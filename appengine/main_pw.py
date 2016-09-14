# -*- coding: utf-8 -*-

# Default modules
import json
import logging
import time

# Additional modules
import flask
from google.appengine.api import taskqueue
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
from google.appengine.api import app_identity


ZONE = "us-central1-b"

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

app = flask.Flask(__name__)
app.config.update(
    DEBUG=False,
    JSON_AS_ASCII=False,
)


@app.route("/pw/hello", methods=["GET"])
def hello():
    return "hello"


@app.route("/pw/add-pull-queues", methods=["POST"])
def add_pull_queues():
    queues = flask.request.get_json()["queues"]
    tasks = [taskqueue.Task(payload=json.dumps(i), method="PULL") for i in queues]
    q = taskqueue.Queue("pull-queue")
    q.add(tasks)
    return "ok"


@app.route("/pw/manage-workers", methods=["GET"])
def manage_workers():
    q = taskqueue.Queue()
    task = taskqueue.Task(url="/pw/tq/manage-workers", method="GET")
    q.add(task)
    return "ok"


@app.route("/pw/tq/manage-workers", methods=["GET"])
def tq_manage_workers():
    credentials = GoogleCredentials.get_application_default()
    compute_api = discovery.build("compute", "v1", credentials=credentials)
    start = t = time.time()
    while True:
        # Control the number of the instances every one minute
        if time.time() - t >= 5:
            t = time.time()
            control_n_instances(compute_api)
            logger.debug(count_pull_queues())
    return "ok"


def count_pull_queues():
    q = taskqueue.Queue('pull-queue')
    n_queues = len(q.lease_tasks(lease_seconds=0, max_tasks=1000))
    logger.info("the numbers of pull queues: {}".format(n_queues))
    return n_queues


def count_instances(compute_api):
    project = app_identity.get_application_id()
    # Count the number of instances in group
    request_get = compute_api.instanceGroupManagers().get(
        project=project,
        zone=ZONE,
        instanceGroupManager="preemptible-workers"
    )
    result_get = request_get.execute()
    logger.debug(result_get)
    n_instances = result_get["targetSize"]
    return n_instances


def control_n_instances(compute_api):
    n_available_tasks = count_pull_queues()
    project = app_identity.get_application_id()
    n_instances = count_instances(compute_api)
    # Add an instance if available task exists
    # if n_available_tasks >= 2:
    #     logger.info("increase the number of the instances")
    #     request_resize = compute_api.instanceGroupManagers().resize(
    #         project=project,
    #         zone=ZONE,
    #         instanceGroupManager="preemptible-workers",
    #         size=n_instances+n_available_tasks-1
    #     )
    #     result_resize = request_resize.execute()
    #     logger.debug(result_resize)
    #     return result_resize
    if n_available_tasks == 0:
        logger.info("decrease the number of the instances")
        request_resize = compute_api.instanceGroupManagers().resize(
            project=project,
            zone=ZONE,
            instanceGroupManager="preemptible-workers",
            size=max(1, n_instances-1)
        )
        result_resize = request_resize.execute()
        logger.debug(result_resize)
        return result_resize
    else:
        return None
