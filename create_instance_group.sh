#!/usr/bin/env bash

# Get project id
PROJECT_ID=`gcloud config list project --format "value(core.project)"`

# Upload Python script
gsutil cp consume_tasks.py gs://${PROJECT_ID}.appspot.com/tmp/

# Create instance template
gcloud compute --project ${PROJECT_ID} instance-templates create "preemptible-worker" \
  --machine-type "n1-standard-1" \
  --network "default" \
  --no-restart-on-failure \
  --maintenance-policy "TERMINATE" \
  --preemptible \
  --scopes default="https://www.googleapis.com/auth/logging.write","https://www.googleapis.com/auth/monitoring.write","https://www.googleapis.com/auth/servicecontrol","https://www.googleapis.com/auth/service.management.readonly","https://www.googleapis.com/auth/devstorage.full_control","https://www.googleapis.com/auth/taskqueue" \
  --tags "http-server","https-server" \
  --image "/ubuntu-os-cloud/ubuntu-1404-trusty-v20160809a" \
  --boot-disk-size "10" \
  --boot-disk-type "pd-standard" \
  --boot-disk-device-name "preemptible-worker" \
  --metadata-from-file startup-script=startup.sh

# Create instance group
gcloud compute --project ${PROJECT_ID} instance-groups managed create "preemptible-workers" \
  --zone "us-central1-b" \
  --base-instance-name "preemptible-workers" \
  --template "preemptible-worker" \
  --size "0"
