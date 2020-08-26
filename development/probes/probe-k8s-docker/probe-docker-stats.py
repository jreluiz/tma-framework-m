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
    # try:
    #     data = run(f"docker stats {container_name} --no-stream")
    # except:
    #     data = run(f"docker stats --no-stream")
    data = run(f"docker stats --no-stream")
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
    if len(container_metrics) == 0:
        container_metrics = [
            '0.00',
            '0.00'
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
    if metrics[0] == '0.00':
        cpu_usage = float(0.00)
    else:
        cpu_usage = float(metrics[0]) / 100
    obs = Observation(time=int(time.time()), value=cpu_usage)
    dt.add_observation(observation=obs)
    message.add_data(data=dt)

    # add memory metric
    dt = Data(type="measurement", descriptionId=104, metricId=7, observations=None)
    if metrics[1] == '0.00':
        memory_usage = float(0.00)
    else:
        memory_usage = float(metrics[1]) / 100
    obs = Observation(time=int(time.time()), value=memory_usage)
    dt.add_observation(observation=obs)
    message.add_data(data=dt)

    # return message formatted in json
    return json.dumps(message.reprJSON(), cls=ComplexEncoder)


# send stat to API server
def send_stat(metrics, url, communication, messageId):
    # if len(metrics) > 0 and metrics[0] != '0.00' and metrics[1] != '0.00':
    # format the stats from container
    stat_formatted = format(metrics, messageId)
    print(f'---Sending message to monitor: {stat_formatted}')

    url = 'http://0.0.0.0:5000/monitor'
    response = communication.send_message(stat_formatted)


# get stats from container
def get_container_stats(container_name, url, communication):
    messageId = 1
    while (True):
        container_metrics = get_stats(container_name)
        print(container_metrics)
        send_stat(container_metrics, url, communication, messageId)
        messageId += 1

        time.sleep(14)


if __name__ == "__main__":
    container_name = str(sys.argv[1] + '')
    url = str(sys.argv[2] + '')

    communication = Communication(url)
    get_container_stats(container_name, url, communication)
