#!/usr/bin/python
import json
import subprocess

import docker
import sys
import time

from communication import Communication
from data import Data
from message import ComplexEncoder
from message import Message
from observation import Observation


def run(cmd):
    res = subprocess.check_output(cmd, shell=True)
    return res


# is container alive
def is_container_alive(container_name, url, communication):
    # connect to docker

    try:
        # try connect to container
        client = docker.APIClient(base_url='unix://var/run/docker.sock')
        inspect_result = client.inspect_container(container_name)
        status = inspect_result.get('State', None).get('Status', None)
        print(status)
        if status == 'running':
            return True
    except docker.errors.APIError:
        pass

    return False


def format(metric_value, messageId):
    """"Format message to send."""
    # message to sent to the server API (follow the json schema)
    message = Message(probeId=201, resourceId=202, messageId=messageId, sentTime=int(time.time()), data=None)

    # add cpu metric
    dt = Data(type="measurement", descriptionId=203, metricId=10, observations=None)

    obs = Observation(time=int(time.time()), value=metric_value)
    dt.add_observation(observation=obs)
    message.add_data(data=dt)

    # return message formatted in json
    return json.dumps(message.reprJSON(), cls=ComplexEncoder)


# send metrics to API server
def send_metrics(metric_value, url, communication, messageId):
    # format the metrics from container
    metric_formatted = format(metric_value, messageId)
    print(f'---Sending message to monitor: {metric_formatted}')

    response = communication.send_message(metric_formatted)


def verify_container_activity(container_name, url, communication):
    """Verify container activity."""
    messageId = 1
    failures = 1
    while (True):
        container_alive = is_container_alive(container_name, url, communication)
        metric_value = 0.0
        if not container_alive:
            metric_value = 0.1
            metric_value *= failures
            failures += 1

        send_metrics(metric_value, url, communication, messageId)

        messageId += 1
        if metric_value >= 0.3:
            time.sleep(20)
        time.sleep(5)


if __name__ == "__main__":
    container_name = str(sys.argv[1] + '')
    url = str(sys.argv[2] + '')

    communication = Communication(url)
    verify_container_activity(container_name, url, communication)
