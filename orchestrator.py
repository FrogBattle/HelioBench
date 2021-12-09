from subprocess import run
from time import time
from data_collector import collect_metrics

MICROSERVICES_TO_RUN = ['go-api','memcached']
DOCKER_COMPOSE_COMMAND = 'docker-compose up --build --abort-on-container-exit'

def orchestrate():
    for service in MICROSERVICES_TO_RUN:
        print(service)
        experiment_start_epoch = time()
        run(DOCKER_COMPOSE_COMMAND, shell=True, cwd=f'./microservices/{service}')
        experiment_end_epoch = time()

        # Experiment has finished
        query = "avg by (instance) (irate(node_cpu_seconds_total{mode='system'}[1m])) * 100"
        raw_data = collect_metrics(query, experiment_start_epoch, experiment_end_epoch)

if __name__ == '__main__':
    orchestrate()