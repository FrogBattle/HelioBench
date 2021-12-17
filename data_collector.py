import requests
from time import time
import csv

PROMETHEUS_URL = 'http://localhost:{port}/api/v1/query_range'
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
        if(self.service): return f'{self.message}: {self.service}'
        return self.message

def collect_metrics(prometheus_port, query, start_time = time() - ONE_DAY_IN_SECONDS, end_time = time(), step = 15):
    query = "avg by (instance) (irate(node_cpu_seconds_total{mode='system'}[1m])) * 100"

    if start_time >= end_time:
        return []
    
    response = attempt_step(prometheus_port, query, start_time, end_time, step)

    if('status' in response and response['status'] == 'success'):
        if('data' in response and 'result' in response['data'] and len(response['data']['result']) == 0):
            return []
            
        return response['data']['result'][0]['values']
    else:
        if response['errorType'] == 'bad_data' and 'exceeded maximum resolution' in response['error']:
            middle_time = start_time + (end_time - start_time) / 2
            res_part_1 = collect_metrics(prometheus_port, query, start_time, middle_time, step)
            res_part_1.extend(collect_metrics(prometheus_port, query, middle_time, end_time, step))
            return res_part_1
        else: 
            print(f"Error collecting data for query: {query}", response)
            raise MetricCollectionError()

def attempt_step(prometheus_port, query, start, end, step):
    response = requests.get(
        PROMETHEUS_URL.format(port=prometheus_port),
        params = {"query":query, "start": start, "end":end, "step":step}).json()
    return response


if __name__ == '__main__':
    query = "avg by (instance) (irate(node_cpu_seconds_total{mode='system'}[1m])) * 100"
    res = collect_metrics(query)
    print(f'Collected {len(res)} total datapoints for query:{query}')
    title = ['query', query]
    header = ['epoch', 'result']

    print("saving to file")
    with open('result.csv', 'w') as f:
        writer = csv.writer(f)

        writer.writerow(title)
        writer.writerow(header)

        writer.writerows(res)