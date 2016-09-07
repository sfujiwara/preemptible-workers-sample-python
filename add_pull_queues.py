# -*- coding: utf-8 -*-

import subprocess
import requests

PROJECT_ID = subprocess.check_output(
    "gcloud config list project --format 'value(core.project)'",
    shell=True
).rstrip()
URL = "https://{}.appspot.com/add-pull-queues".format(PROJECT_ID)

payload = {"queues": []}
for i in range(100):
    payload["queues"].append({"file": "file{}".format(i)})
requests.post(URL, json=payload)
