import json
import csv
from json.decoder import JSONDecodeError
from os import makedirs, path
from time import  time, sleep
from config_parser import parse_and_validate_config, parse_service_envvars
from data_collector import MetricCollectionError, collect_metrics
from asyncio import create_subprocess_shell, run
from asyncio.subprocess import PIPE
from subprocess import run as cmd_run
from datetime import datetime

DEFAULT_PROMETHEUS_PORT = '9900'

LOCAL_SCRIPTS_FOLDER = '$(pwd)/scripts/'
LOGS_FOLDER = './logs/'
RESULTS_FOLDER = './results/'
CONTAINER_SCRIPTS_FOLDER = '/home/scripts/'
DOCKER_COMPOSE_COMMAND = 'docker-compose up --build'
DOCKER_VOLUME_NAME = 'HelioBench'
DOCKER_COMPOSE_VOLUME_PATH = f'/var/lib/docker/volumes/{DOCKER_VOLUME_NAME}/_data'
QUERY_MAPPING = {
    'CPU_USER_PRC': "avg by (instance) (irate(node_cpu_seconds_total{mode='user'}[1m])) * 100",
    'CPU_SYS_PRC':  "avg by (instance) (irate(node_cpu_seconds_total{mode='system'}[1m])) * 100",
    'CPU_IDLE_PRC': "avg by (instance) (irate(node_cpu_seconds_total{mode='idle'}[1m])) * 100",
    'MEM_FREE_PRC': "avg by (instance) (node_memory_MemFree_bytes / node_memory_MemTotal_bytes) * 100",
    'MEM_USED_PRC': "avg by (instance) ((node_memory_MemTotal_bytes - node_memory_MemFree_bytes - node_memory_Buffers_bytes - node_memory_Cached_bytes) / node_memory_MemTotal_bytes) * 100",
    'IO_READS_PS':  "avg by (instance) (rate(node_disk_reads_completed_total[5m]))",
    'IO_WRITES_PS':    "avg by (instance) (rate(node_disk_writes_completed_total[5m]))",
    'IO_READ_KBPS':    "avg by (instance) (rate(node_disk_read_bytes_total[5m]))",
    'IO_WRITE_KBPS':   "avg by (instance) (rate(node_disk_write_bytes_total[5m])",
}

def run_auxiliary_script(script_name, parameters = '', text=False):
    return cmd_run(f'''
        docker run --rm -it \
        -v {DOCKER_VOLUME_NAME}:/home/experiment \
        -v {LOCAL_SCRIPTS_FOLDER}{script_name}:{CONTAINER_SCRIPTS_FOLDER}{script_name} \
        python:3.9 python3 {CONTAINER_SCRIPTS_FOLDER}{script_name} {parameters}''',
        shell=True, capture_output=True, text=text)

def collect_process_metrics_query(service_details, query, query_name):
    prometheus_port = service_details['environment'].get('PROMETHEUS_PORT', DEFAULT_PROMETHEUS_PORT)
    res = collect_metrics(prometheus_port, query, service_details['start_time'], service_details['end_time'], step=1)

    print(f'Collected {len(res)} datapoints for query: {query_name}')
    title = ['query', query_name]
    header = ['epoch', 'result']
    
    
    dir_path = f"{RESULTS_FOLDER}/{service_details['service']}/"
    if not path.exists(dir_path):
        makedirs(dir_path)

    with open(f"{dir_path}{query_name}.csv", 'w+') as f:
        writer = csv.writer(f)

        writer.writerow(title)
        writer.writerow(header)

        writer.writerows(res)

def collect_all_service_metrics(service_details):
    print(f"Collecting metrics for {service_details['service']}")
    for query_name, query in QUERY_MAPPING.items():
        collect_process_metrics_query(service_details, query, query_name)

async def run_benchmark(service):
    process = await create_subprocess_shell(
        DOCKER_COMPOSE_COMMAND, cwd=f'./microservices/{service}',
        stdout=PIPE, stderr=PIPE)
    return process

async def collect_logs(service, process):
    service_dir = f'{LOGS_FOLDER}{service}/'
    if not path.exists(service_dir):
        makedirs(service_dir)

    stdout_filename = f'{service_dir}log.log'
    stderr_filename = f'{service_dir}log.error'
    
    if process.stdout:
        with open(stdout_filename,'wb+') as file:
            line = await process.stdout.readline()
            while not process.stdout.at_eof() and len(line) != 0:
                file.write(line)
                line = await process.stdout.readline()

    if process.stderr:
        with open(stderr_filename,'wb+') as file:
            while not process.stderr.at_eof():
                stderr_data_line = await process.stderr.readline()
                file.write(stderr_data_line)

async def orchestrate(services, service_envvars):
    experiment_start_time = time()
    try:
        processes = {}
        completed_processes = {}
        for service in services:
            new_proc = await run_benchmark(service)
            processes[service] = {
                "service":service, "process":new_proc, "start_time":time(),
                "environment":service_envvars[service] if service in service_envvars else {}
                }
            print(f"Started process for {service}")
        
        sleep(5)
        while True:
            result = json.loads(run_auxiliary_script('poll_for_finish_files.py').stdout)

            duration = datetime.fromtimestamp(time() - experiment_start_time)
            print("Experiment running:", duration.strftime('%H:%M:%S'), end='\r')

            if('status' in result and 'filenames' in result and result['status'] == 'success'):
                finished_services = result['filenames']
                for finished_service in finished_services:
                    finished_service_name = finished_service.split('.')[0]
                    if finished_service_name in processes:
                        print(f"Service {finished_service_name} finished")
                        processes[finished_service_name]['end_time'] = time()
                        collect_all_service_metrics(processes[finished_service_name])
                        processes[finished_service_name]['process'].terminate()
                        completed_processes[finished_service_name] = processes.pop(finished_service_name)

            if len(processes) == 0:
                print("Experiment finished")
                return

            sleep(5)

    except KeyboardInterrupt:
        print("\nExperiment cancelled")
    except (JSONDecodeError, TypeError, MetricCollectionError) as e:
        print(e)
        print("Error polling files for data...Killing processes")
        for service_details in processes.values():
            service_details['process'].terminate()
    finally:
        print("Collecting logs for processes...")
        for service_details in [*processes.values(), *completed_processes.values()]:
            await collect_logs(service_details['service'], service_details['process'])        

async def main():
    config = parse_and_validate_config()
    services = list(config['services'].keys())
    service_envvars = parse_service_envvars(config)
    print(service_envvars)

    print(run_auxiliary_script('remove_finished_volumes.py', ' '.join(services), True).stdout)
    await orchestrate(services, service_envvars)

run(main())