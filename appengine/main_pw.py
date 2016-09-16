# -*- coding: utf-8 -*-

# Default modules
import json
import logging

# Additional modules
import flask
from google.appengine.api import taskqueue
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
from google.appengine.api import app_identity


PROJECT_ID = app_identity.get_application_id()
ZONE = "us-central1-b"
QUEUE_NAME = "pull-queue"
INSTANCE_GROUP_NAME = "preemptible-workers"

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

app = flask.Flask(__name__)
app.config.update(
    DEBUG=False,
    JSON_AS_ASCII=False,
)


@app.route("/pw/add-pull-queues", methods=["POST"])
def add_pull_queues():
    queues = flask.request.get_json()["tasks"]
    tasks = [taskqueue.Task(payload=json.dumps(i), method="PULL") for i in queues]
    q = taskqueue.Queue(QUEUE_NAME)
    q.add(tasks)
    return "ok"


@app.route("/pw/cron/resize-instance-group", methods=["GET"])
def resize_instance_group():
    # Count the number of tasks
    n_tasks = taskqueue.Queue(QUEUE_NAME).fetch_statistics().tasks
    # Resize the number of instances
    credentials = GoogleCredentials.get_application_default()
    compute_api = discovery.build("compute", "v1", credentials=credentials)
    request_resize = compute_api.instanceGroupManagers().resize(
        project=PROJECT_ID,
        zone=ZONE,
        instanceGroupManager=INSTANCE_GROUP_NAME,
        size=n_tasks,
    )
    result_resize = request_resize.execute()
    logger.debug("Resize the instance group: {}".format(result_resize))
    return "ok"


# def count_instances(compute_api):
#     project = app_identity.get_application_id()
#     # Count the number of instances in group
#     request_get = compute_api.instanceGroupManagers().get(
#         project=project,
#         zone=ZONE,
#         instanceGroupManager=INSTANCE_GROUP_NAME
#     )
#     result_get = request_get.execute()
#     logger.debug(result_get)
#     n_instances = result_get["targetSize"]
#     return n_instances
