from os import path, makedirs
import requests
from time import time
import argparse
import sys
import csv

ONE_SECOND = 1
ONE_MINUTE_IN_SECONDS = 60 * ONE_SECOND
ONE_HOUR_IN_SECONDS = 60 * ONE_MINUTE_IN_SECONDS
ONE_DAY_IN_SECONDS = 24 * ONE_HOUR_IN_SECONDS


class MetricCollectionError(Exception):
    def __init__(self, service=None, message="Error collecting metrics for service"):
        self.service = service
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        if(self.service):
            return f'{self.message}: {self.service}'
        return self.message


def collect_metrics(prometheus_hostname, prometheus_port, query, start_time=time() - ONE_DAY_IN_SECONDS, end_time=time(), step=15):
    if start_time >= end_time:
        return []

    response = attempt_step(prometheus_hostname, prometheus_port, query, start_time, end_time, step)

    if('status' in response and response['status'] == 'success'):
        if('data' in response and 'result' in response['data'] and len(response['data']['result']) == 0):
            return []

        return response['data']['result'][0]['values']
    else:
        if response['errorType'] == 'bad_data' and 'exceeded maximum resolution' in response['error']:
            middle_time = start_time + (end_time - start_time) / 2
            res_part_1 = collect_metrics(prometheus_hostname, prometheus_port, query, start_time, middle_time, step)
            res_part_1.extend(collect_metrics(prometheus_hostname, prometheus_port, query, middle_time, end_time, step))
            return res_part_1
        else:
            print(f"Error collecting data for query: {query}", response)
            raise MetricCollectionError()


def attempt_step(prometheus_hostname, prometheus_port, query, start, end, step):
    response = requests.get(
        f"http://{prometheus_hostname}:{prometheus_port}/api/v1/query_range",
        params={"query": query, "start": start, "end": end, "step": step}).json()
    return response


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Standalone data collector for Prometheus endpoints')
    parser.add_argument('-n', '--hostname', required=True, help="The hostname of the Prometheus server")
    parser.add_argument('-p', '--port', required=True, help="The port of the Prometheus server")
    parser.add_argument('-q', '--query', required=True, help="The query to be retrieved from the server")
    parser.add_argument('-s', '--start-time', required=True, help="The epoch start time from which to consider results")
    parser.add_argument('-e', '--end-time', required=True, help="The epoch end time from which to consider results")

    parsed_args = parser.parse_args(sys.argv[1:])
    prometheus_hostname = parsed_args.hostname
    prometheus_port = parsed_args.port
    query_name = parsed_args.query
    start_time = parsed_args.start_time
    end_time = parsed_args.end_time
    prometheus_hostname = parsed_args.hostname

    res = collect_metrics(prometheus_hostname, prometheus_port, query_name, start_time, end_time, step=1)

    title = ['query', query_name]
    header = ['epoch', 'result']

    dir_path = f"./{time()}/"
    if not path.exists(dir_path):
        makedirs(dir_path)

    with open(f"{dir_path}{query_name}.csv", 'w+') as f:
        writer = csv.writer(f)

        writer.writerow(title)
        writer.writerow(header)

        writer.writerows(res)
