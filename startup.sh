#!/usr/bin/env bash

apt-get update
apt-get -y upgrade
apt-get -y install python-dev
apt-get -y install python-pip
apt-get -y install git

# Install Python packages
pip install gcloud
pip install google-api-python-client
pip install git+https://github.com/sfujiwara/gjhandler.git

# Install google-fluentd
curl -sSO https://dl.google.com/cloudagents/install-logging-agent.sh
sha256sum install-logging-agent.sh
sudo bash install-logging-agent.sh

# Create config file for google-fluentd
FLUENTD_CONF_FILE="/etc/google-fluentd/config.d/python.conf"
echo "<source>" > ${FLUENTD_CONF_FILE}
echo "  type tail" >> ${FLUENTD_CONF_FILE}
echo "  format json" >> ${FLUENTD_CONF_FILE}
echo "  path /var/log/python/*.log,/var/log/python/*.json" >> ${FLUENTD_CONF_FILE}
echo "  read_from_head true" >> ${FLUENTD_CONF_FILE}
echo "  tag python" >> ${FLUENTD_CONF_FILE}
echo "</source>" >> ${FLUENTD_CONF_FILE}

# Create log directory for Python script
mkdir -p /var/log/python

# Restart google-fluentd
service google-fluentd restart

# Run python script
PROJECT_ID=`curl "http://metadata.google.internal/computeMetadata/v1/project/project-id" -H "Metadata-Flavor: Google"`
PYTHON_SCRIPT="consume_tasks.py"
cd /tmp
gsutil cp gs://${PROJECT_ID}.appspot.com/tmp/${PYTHON_SCRIPT} /tmp/
python ${PYTHON_SCRIPT}
