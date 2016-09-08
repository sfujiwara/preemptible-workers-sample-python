# -*- coding: utf-8 -*-

import base64
import logging
import traceback
import time
import subprocess
import json

from googleapiclient.discovery import build
from oauth2client.client import GoogleCredentials
# from gcloud import storage

import gjhandler

PROJECT_ID = subprocess.check_output(
    "gcloud config list project --format 'value(core.project)'",
    shell=True
).rstrip()
BUCKET_NAME = "{}.appspot.com".format(PROJECT_ID)
TASKQUEUE_NAME = "pull-queue"

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(gjhandler.GoogleJsonHandler("/var/log/python/log.json"))


def consume_task(task_api, item):
    task = base64.b64decode(item["payloadBase64"])
    time.sleep(120)


def lease_task(task_api):
    try:
        lease_req = task_api.tasks().lease(
            project=PROJECT_ID,
            taskqueue=TASKQUEUE_NAME,
            leaseSecs=240,
            numTasks=1,
        )
        result = lease_req.execute()
        return result
    except Exception as e:
        logger.error(traceback.format_exc())
        return {}


def delete_task(task_api, item):
    try:
        delete_request = task_api.tasks().delete(
            project="s~"+PROJECT_ID,
            taskqueue=TASKQUEUE_NAME,
            task=str(item["id"])
        )
        delete_request.execute()
    except Exception as e:
        logger.error(traceback.format_exc())


def extend_lease_time(task_api, item):
    item = dict(item)
    item["queueName"] = item["queueName"].split("/")[-1]
    logger.info("body: {}".format(json.dumps(item)))
    try:
        update_request = task_api.tasks().update(
            project=PROJECT_ID,
            taskqueue=TASKQUEUE_NAME,
            task=str(item["id"]),
            newLeaseSeconds=60,
            body=item
        )
        update_request.execute()
        logger.info("update lease seconds")
    except Exception as e:
        logger.error(traceback.format_exc())


def main():
    credentials = GoogleCredentials.get_application_default()
    task_api = build("taskqueue", "v1beta2", credentials=credentials)
    while True:
        # Lease a task from pull queues
        task = lease_task(task_api)
        # Wait if available task does not exist
        if "items" not in task:
            logger.info("wait")
            time.sleep(60)
        else:
            item = task["items"][0]
            logger.info("consume task: {}".format(item))
            consume_task(task_api, item)
            delete_task(task_api, item)
            logger.info("complete and delete task: {}".format(item))
            # bucket = storage.Client().get_bucket(BUCKET_NAME)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(traceback.format_exc())
