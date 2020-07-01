#!/usr/bin/python
import json
import subprocess
import docker
import sys
from datetime import datetime
import requests
import time
from communication import Communication
from data import Data
from message import Message
from message import ComplexEncoder
from observation import Observation


def run(cmd):
    res = subprocess.check_output(cmd, shell=True)
    return res


def get_stats(container_name):
    data = run(f"docker stats {container_name} --no-stream")
    container_metrics = []
    lines = data.decode('UTF-8').split("\n")
    for line in lines[1:]:
        bits = line.split("  ")
        bits = [bit for bit in bits if bit.strip() != ""]
        if len(bits) == 8:
            # print("0", bits[0])
            # print("1", bits[1])
            # print("2", bits[2])
            # print("3", bits[3].split("/")[1].strip().replace("MiB", ""))
            # print("4", bits[4])
            # print("5", bits[5])
            # print("6", bits[6])
            # print("7", bits[7])
            container_metrics = [
                bits[2].strip().replace("%", ""),
                bits[4].strip().replace("%", "")
            ]
    return container_metrics


# format stat to
def format(metrics, messageId):
    # the timestamp is the same for all metrics from this stat variable (Python is not compatible with nanoseconds,
    #  so [:-4] -> microseconds)
    # timestamp = int(time.mktime(datetime.strptime(stat['read'][:-4], '%Y-%m-%dT%H:%M:%S.%f').timetuple()))

    # message to sent to the server API
    # follow the json schema
    # sentTime = current time? Or the same timestamp from the metrics?
    # need to change the probeId, resourceId and messageId
    message = Message(probeId=101, resourceId=102, messageId=messageId, sentTime=int(time.time()), data=None)

    # add cpu metric
    dt = Data(type="measurement", descriptionId=103, metricId=6, observations=None)
    obs = Observation(time=int(time.time()), value=metrics[0])
    dt.add_observation(observation=obs)
    message.add_data(data=dt)

    # add memory metric
    dt = Data(type="measurement", descriptionId=104, metricId=7, observations=None)
    obs = Observation(time=int(time.time()), value=metrics[1])
    dt.add_observation(observation=obs)
    message.add_data(data=dt)

    # return message formatted in json
    return json.dumps(message.reprJSON(), cls=ComplexEncoder)


# send stat to API server
def send_stat(metrics, url, communication, messageId):
    # format the stats from container
    stat_formatted = format(metrics, messageId)
    print(f'---Sending message to monitor: {stat_formatted}')

    # url = 'http://0.0.0.0:5000/monitor'
    # response = communication.send_message(stat_formatted)


# get stats from container
def get_container_stats(container_name, url, communication):
    messageId = 1
    while (True):
        container_metrics = get_stats(container_name)
        send_stat(container_metrics, url, communication, messageId)
        messageId += 1

        time.sleep(3)


if __name__ == "__main__":
    container_name = str(sys.argv[1] + '')
    url = str(sys.argv[2] + '')

    communication = Communication(url)
    get_container_stats(container_name, url, communication)
