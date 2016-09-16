# -*- coding: utf-8 -*-

import subprocess
import requests


# Get project ID from gcloud config
project_id = subprocess.check_output(
    "gcloud config list project --format 'value(core.project)'",
    shell=True
).rstrip()

# Add pull queues to App Engine
url = "https://{}.appspot.com/pw/add-pull-queues".format(project_id)
payload = {"tasks": []}
for i in range(3):
    payload["tasks"].append({"file": "file{}".format(i)})
res = requests.post(url, json=payload)
