import docker
import ast
import sys
import json
import time
from datetime import datetime
import requests
from tmalibrary.probes import *
from subprocess import call
import json
import os
import subprocess

# get stats from container
def get_container_stats(container_name, url, communication):
    # connect to docker
    cli = docker.from_env()
    # get container
    container = cli.containers.get(container_name)
    # get stream of stats from container
    stats_obj = container.stats()

    for stat in stats_obj:
        # print the response
        send_stat(eval(stat), url, communication, container)


# send stat to API server
def send_stat(stat, url, communication, container):
    # format the stats from container
    stat_formatted = format(stat)

    # percentage_memory_usage = percentage(stat['memory_stats']['usage'], stat['memory_stats']['limit'])
    # print(percentage_memory_usage)
    # if percentage_memory_usage > 90:
    #     container.update(mem_limit='300MB')

    # print(f"Memory usage {humansize(stat['memory_stats']['usage'])}")
    # print(f"Memory limit {humansize(stat['memory_stats']['limit'])}")
    # print(f"Percentage usage: {percentage(stat['memory_stats']['usage'], stat['memory_stats']['limit'])}")
    # print(f"Memory max usage {humansize(stat['memory_stats']['max_usage'])}")

    # print(stat['cpu_stats']['online_cpus'])
    # print(f"cpu percent: {calculate_cpu_percent(stat)}")
    # print(f"cpu total_usage {stat['cpu_stats']['cpu_usage']['total_usage']}")
    # print(f"cpu percpu_usage {stat['cpu_stats']['cpu_usage']['percpu_usage'][0]}")

    # print(calculate_cpu_percent2(stat, 0, 0))

    # print(stat['cpu_stats'])

    # url = 'http://0.0.0.0:5000/monitor'
    #response = communication.send_message(stat_formatted)

# this is taken directly from docker client:
#   https://github.com/docker/docker/blob/28a7577a029780e4533faf3d057ec9f6c7a10948/api/client/stats.go#L309
def calculate_cpu_percent(d):
    cpu_count = len(d["cpu_stats"]["cpu_usage"]["percpu_usage"])
    cpu_percent = 0.0
    cpu_delta = float(d["cpu_stats"]["cpu_usage"]["total_usage"]) - \
                float(d["precpu_stats"]["cpu_usage"]["total_usage"])
    system_delta = float(d["cpu_stats"]["system_cpu_usage"])

    if system_delta > 0.0:
        cpu_percent = cpu_delta / system_delta * 100.0 * cpu_count
    return cpu_percent

def calculate_cpu_percent2(d, previous_cpu, previous_system):
    # import json
    # du = json.dumps(d, indent=2)
    # logger.debug("XXX: %s", du)
    cpu_percent = 0.0
    cpu_total = float(d["cpu_stats"]["cpu_usage"]["total_usage"])
    cpu_delta = cpu_total - previous_cpu
    cpu_system = float(d["cpu_stats"]["system_cpu_usage"])
    system_delta = cpu_system - previous_system
    online_cpus = d["cpu_stats"].get("online_cpus", len(d["cpu_stats"]["cpu_usage"]["percpu_usage"]))
    if system_delta > 0.0:
        cpu_percent = (cpu_delta / system_delta) * online_cpus * 100.0
    return cpu_percent, cpu_system, cpu_total

def percentage(part, whole):
  return 100 * float(part)/float(whole)

suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
def humansize(nbytes):
    i = 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])

# format stat to
def format(stat):
    # st = [-1] * 96
    # sometimes the following metrics can be empty (reboot can fix it). -1 -> empty
    # if len(stat['blkio_stats']['io_service_bytes_recursive']) > 0:
    #     for i in range(0,15,3):
    #         st[i] = stat['blkio_stats']['io_service_bytes_recursive'][i/3]['major']
    #         st[i+1] = stat['blkio_stats']['io_service_bytes_recursive'][i/3]['minor']
    #         st[i+2] = stat['blkio_stats']['io_service_bytes_recursive'][i/3]['value']
    #
    # if len(stat['blkio_stats']['io_serviced_recursive']) > 0:
    #     for i in range (15,30,3):
    #         st[i] = stat['blkio_stats']['io_serviced_recursive'][i/3-5]['major']
    #         st[i+1] = stat['blkio_stats']['io_serviced_recursive'][i/3-5]['minor']
    #         st[i+2] = stat['blkio_stats']['io_serviced_recursive'][i/3-5]['value']
    #
    # if len(stat['blkio_stats']['io_queue_recursive']) > 0:
    #     for i in range(30,45,3):
    #         st[i] = stat['blkio_stats']['io_queue_recursive'][i/3-10]['major']
    #         st[i+1] = stat['blkio_stats']['io_queue_recursive'][i/3-10]['minor']
    #         st[i+2] = stat['blkio_stats']['io_queue_recursive'][i/3-10]['value']
    #
    # if len(stat['blkio_stats']['io_service_time_recursive']) > 0:
    #     for i in range(45,60,3):
    #         st[i] = stat['blkio_stats']['io_service_time_recursive'][i/3-15]['major']
    #         st[i+1] = stat['blkio_stats']['io_service_time_recursive'][i/3-15]['minor']
    #         st[i+2] = stat['blkio_stats']['io_service_time_recursive'][i/3-15]['value']
    #
    # if len(stat['blkio_stats']['io_wait_time_recursive']) > 0:
    #     for i in range(60,75,3):
    #         st[i] = stat['blkio_stats']['io_wait_time_recursive'][i/3-20]['major']
    #         st[i+1] = stat['blkio_stats']['io_wait_time_recursive'][i/3-20]['minor']
    #         st[i+2] = stat['blkio_stats']['io_wait_time_recursive'][i/3-20]['value']
    #
    # if len(stat['blkio_stats']['io_merged_recursive']) > 0:
    #     for i in range(75,90,3):
    #         st[i] = stat['blkio_stats']['io_merged_recursive'][i/3-25]['major']
    #         st[i+1] = stat['blkio_stats']['io_merged_recursive'][i/3-25]['minor']
    #         st[i+2] = stat['blkio_stats']['io_merged_recursive'][i/3-25]['value']
    #
    # if len(stat['blkio_stats']['io_time_recursive']) > 0:
    #     st[90] = stat['blkio_stats']['io_time_recursive'][0]['major']
    #     st[91] = stat['blkio_stats']['io_time_recursive'][0]['minor']
    #     st[92] = stat['blkio_stats']['io_time_recursive'][0]['value']
    #
    # if len(stat['blkio_stats']['sectors_recursive']) > 0:
    #     st[93] = stat['blkio_stats']['sectors_recursive'][0]['major']
    #     st[94] = stat['blkio_stats']['sectors_recursive'][0]['minor']
    #     st[95] = stat['blkio_stats']['sectors_recursive'][0]['value']

    other_st = [
        stat['num_procs'],
        stat['cpu_stats']['cpu_usage']['total_usage'],
        stat['cpu_stats']['cpu_usage']['percpu_usage'][0],
        stat['cpu_stats']['cpu_usage']['usage_in_kernelmode'],
        stat['cpu_stats']['cpu_usage']['usage_in_usermode'],
        stat['cpu_stats']['system_cpu_usage'],
        stat['cpu_stats']['online_cpus'],
        stat['cpu_stats']['throttling_data']['periods'],
        stat['cpu_stats']['throttling_data']['throttled_periods'],
        stat['cpu_stats']['throttling_data']['throttled_time'],
        stat['memory_stats']['usage'],
        stat['memory_stats']['max_usage'],
        stat['memory_stats']['stats']['active_anon'],
        stat['memory_stats']['stats']['active_file'],
        stat['memory_stats']['stats']['cache'],
        stat['memory_stats']['stats']['dirty'],
        stat['memory_stats']['stats']['hierarchical_memory_limit'],
        stat['memory_stats']['stats']['inactive_anon'],
        stat['memory_stats']['stats']['inactive_file'],
        stat['memory_stats']['stats']['mapped_file'],
        stat['memory_stats']['stats']['pgfault'],
        stat['memory_stats']['stats']['pgmajfault'],
        stat['memory_stats']['stats']['pgpgin'],
        stat['memory_stats']['stats']['pgpgout'],
        stat['memory_stats']['stats']['rss'],
        stat['memory_stats']['stats']['rss_huge'],
        stat['memory_stats']['stats']['total_active_anon'],
        stat['memory_stats']['stats']['total_active_file'],
        stat['memory_stats']['stats']['total_cache'],
        stat['memory_stats']['stats']['total_dirty'],
        stat['memory_stats']['stats']['total_inactive_anon'],
        stat['memory_stats']['stats']['total_inactive_file'],
        stat['memory_stats']['stats']['total_mapped_file'],
        stat['memory_stats']['stats']['total_pgfault'],
        stat['memory_stats']['stats']['total_pgmajfault'],
        stat['memory_stats']['stats']['total_pgpgin'],
        stat['memory_stats']['stats']['total_pgpgout'],
        stat['memory_stats']['stats']['total_rss'],
        stat['memory_stats']['stats']['total_rss_huge'],
        stat['memory_stats']['stats']['total_unevictable'],
        stat['memory_stats']['stats']['total_writeback'],
        stat['memory_stats']['stats']['unevictable'],
        stat['memory_stats']['stats']['writeback'],
        stat['memory_stats']['limit'],
    ]

    merge_st = other_st

    # the timestamp is the same for all metrics from this stat variable (Python is not compatible with nanoseconds,
    #  so [:-4] -> microseconds)
    timestamp = int(time.mktime(datetime.strptime(stat['read'][:-4], '%Y-%m-%dT%H:%M:%S.%f').timetuple()))

    {"probeId": 8, "resourceId": 8, "messageId": 9, "sentTime": 1593193587519, "data": [
        {"type": "measurement", "descriptionId": 30, "metricId": -1,
         "observations": [{"time": 1593193587, "value": 2.0}]},
        {"type": "measurement", "descriptionId": 31, "metricId": 4,
         "observations": [{"time": 1593193587, "value": 0.3333333333333333}]},
        {"type": "measurement", "descriptionId": 32, "metricId": -1,
         "observations": [{"time": 1593193587, "value": 0.3333333333333333}]},
        {"type": "measurement", "descriptionId": 33, "metricId": -1,
         "observations": [{"time": 1593193587, "value": 0.01650476280298029}]},
        {"type": "measurement", "descriptionId": 34, "metricId": 3,
         "observations": [{"time": 1593193587, "value": 0.2763432282504281}]}]}

    # message to sent to the server API
    # follow the json schema
    # sentTime = current time? Or the same timestamp from the metrics?
    # need to change the probeId, resourceId and messageId
    message = Message(probeId=1, resourceId=1, messageId=0, sentTime=int(time.time()), data=None)

    # add cpu metric
    dt = Data(type="measurement", descriptionId=(i + 1), observations=None)
    obs = Observation(time=timestamp, value=merge_st[i])
    dt.add_observation(observation=obs)
    message.add_data(data=dt)

    # add memory metric

    # append measurement data to message
    for i in range(len(merge_st)):


    # return message formatted in json
    return json.dumps(message.reprJSON(), cls=ComplexEncoder)

def run(cmd):
    res = subprocess.check_output(cmd, shell=True)
    return res

def getStats():
    data = run("docker stats --no-stream")
    containers = {}
    lines = data.split("\n")
    for line in lines[1:]:
        bits = line.split("  ")
        bits = [bit for bit in bits if bit.strip() != ""]
        if len(bits) == 7:
            containers[bits[0]] = {
                    "container": bits[0],
                    "cpu": bits[1],
                    "memory usage": bits[2],
                    "memory %": bits[3],
                    "network i/o": bits[4],
                    "block i/o": bits[5],
                    "pids": bits[6]
                }
    return containers

if __name__ == '__main__':
    # with open("/tmp/output.log", "a") as output:
    # receive the container name and server url as parameters
    container_name = str(sys.argv[1] + '')
    url = str(sys.argv[2] + '')

    print(getStats())

    # test = subprocess.call(f"docker stats {container_name}", shell=True)
    # print("Teste: ", test)

    # communication = Communication(url)
    # get_container_stats(container_name, url, communication)