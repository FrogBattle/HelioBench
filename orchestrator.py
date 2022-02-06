import json
import csv
from json.decoder import JSONDecodeError
from os import environ, makedirs, path
from time import time, sleep

from platformdirs import sys

from deployment import (
    AzureContainerInstanceFactory, build_and_push_docker_compose, build_and_push_single_docker_image, collect_compose_logs,
    delete_storage_finish_files, deploy_docker_compose, ensure_docker_context,
    log_into_container_instances_management, log_into_resource_management, poll_storage_finish_files, stop_compose_process)
from config_parser import (
    PROMETHEUS_CONFIG_FILE_PATH, parse_and_validate_config,
    parse_azure, parse_config, parse_environment,
    parse_service_envvars, save_config, substitute_nested_envvar_strings)
from constants import (
    AZURE_CONTAINER_REGISTRY, AZURE_CONTAINER_REGISTRY_PASSWORD, AZURE_CONTAINER_REGISTRY_USERNAME, AZURE_DOCKER_ACI_CONTEXT,
    AZURE_FILE_SHARE_NAME, AZURE_RESOURCE_GROUP, AZURE_STORAGE_ACCOUNT_KEY,
    AZURE_STORAGE_ACCOUNT_NAME, AZURE_SUBSCRIPTION_ID,
    DEPLOYMENT, DEPLOYMENT_COMPOSE_FILE, EXPERIMENT_WORKLOAD, PROMETHEUS_PORT,
    PROMETHEUS_TARGET_PORT)
from data_collector import MetricCollectionError, collect_metrics
from asyncio import create_subprocess_shell, run
from asyncio.subprocess import PIPE
from subprocess import CalledProcessError, run as cmd_run
from datetime import datetime

DEFAULT_PROMETHEUS_PORT = '9900'
DEFAULT_PROMETHEUS_TARGET_PORT = '9090'
DEFAULT_PROMETHEUS_HOSTNAME = 'localhost'
MICROSERVICES_PATH = './microservices/'
PROMETHEUS_FOLDER = '$(pwd)/microservices/prometheus/'
PROMETHEUS_SERVER_NAME = 'helio-prometheus'

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
    'MEM_USED_PRC': "avg by (instance) ((node_memory_MemTotal_bytes - node_memory_MemFree_bytes - node_memory_Buffers_bytes - node_memory_Cached_bytes)"
    " / node_memory_MemTotal_bytes) * 100",
    'IO_READS_PS':  "avg by (instance) (rate(node_disk_reads_completed_total[5m]))",
    'IO_WRITES_PS':    "avg by (instance) (rate(node_disk_writes_completed_total[5m]))",
    'IO_READ_KBPS':    "avg by (instance) (rate(node_disk_read_bytes_total[5m]))",
    'IO_WRITE_KBPS':   "avg by (instance) (rate(node_disk_written_bytes_total[5m]))",
}


def run_auxiliary_script(script_name, parameters='', text=False):
    return cmd_run(f'''
        docker run --rm -it \
        -v {DOCKER_VOLUME_NAME}:/home/experiment \
        -v {LOCAL_SCRIPTS_FOLDER}{script_name}:{CONTAINER_SCRIPTS_FOLDER}{script_name} \
        python:3.9 python3 {CONTAINER_SCRIPTS_FOLDER}{script_name} {parameters}''',
                   shell=True, capture_output=True, text=text)


def collect_process_metrics_query(prometheus_hostname, prometheus_port, service_details, query, query_name):
    res = collect_metrics(prometheus_hostname, prometheus_port, query,
                          service_details['start_time'], service_details['end_time'], step=1)

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


def collect_all_service_metrics(service_details, prometheus_hostname, prometheus_port):
    print(f"Collecting metrics for {service_details['service']}...")
    for query_name, query in QUERY_MAPPING.items():
        collect_process_metrics_query(prometheus_hostname, prometheus_port, service_details, query, query_name)


async def run_benchmark(service, env):
    process = await create_subprocess_shell(
        DOCKER_COMPOSE_COMMAND, cwd=f'{MICROSERVICES_PATH}{service}',
        stdout=PIPE, stderr=PIPE, env=env)
    return process


async def collect_logs(service, process):
    service_dir = f'{LOGS_FOLDER}{service}/'
    if not path.exists(service_dir):
        makedirs(service_dir)

    stdout_filename = f'{service_dir}log.log'
    stderr_filename = f'{service_dir}log.error'

    if process.stdout:
        with open(stdout_filename, 'wb+') as file:
            line = await process.stdout.readline()
            while not process.stdout.at_eof() and len(line) != 0:
                file.write(line)
                line = await process.stdout.readline()

    if process.stderr:
        with open(stderr_filename, 'wb+') as file:
            while not process.stderr.at_eof():
                stderr_data_line = await process.stderr.readline()
                file.write(stderr_data_line)


def run_prometheus_server():
    print("Starting Prometheus server...")
    cmd_run(f'docker build -t {PROMETHEUS_SERVER_NAME}:latest {PROMETHEUS_FOLDER}', shell=True, stdout=None)
    cmd_run(f'{PROMETHEUS_FOLDER}run_container.sh', shell=True, stdout=None)


def stop_prometheus_server():
    print("Shutting down Prometheus server...")
    cmd_run(f'docker container stop {PROMETHEUS_SERVER_NAME}', shell=True, stdout=None)
    cmd_run(f'docker container rm {PROMETHEUS_SERVER_NAME}', shell=True, stdout=None)


def prepare_prometheus_configuration(service_envvars, is_deployment):
    print("Preparing Prometheus server configuration...")
    prom_config = parse_config(PROMETHEUS_CONFIG_FILE_PATH)

    prom_config['scrape_configs'][0]['static_configs'][0]['targets'] = [
        f'{"localhost" if not is_deployment else f"{service_name}.ukwest.azurecontainer.io"}'
        f':{service_envvars.get(PROMETHEUS_TARGET_PORT, DEFAULT_PROMETHEUS_TARGET_PORT )}'
        for service_name, service_envvars in service_envvars.items() if service_envvars is not None]
    save_config(PROMETHEUS_CONFIG_FILE_PATH, prom_config)


def export_envvars(vars_dict, env=environ.copy()):
    for var_name, var_value in vars_dict.items():
        env[var_name] = substitute_nested_envvar_strings(env, var_value)
    return env


def export_service_envvars(service_envvars, service, env=environ.copy()):
    if service_envvars.get(service, None) is not None:
        env[EXPERIMENT_WORKLOAD] = service
        env = export_envvars(service_envvars.get(service), env)
    return env


def export_deployment_envvars(deployment_config, env=environ.copy()):
    if deployment_config is not None and len(deployment_config) > 0:
        env = export_envvars(deployment_config, env)
    return env


def export_service_and_deployment_envvars(service_envvars, service, deployment_config):
    return export_deployment_envvars(deployment_config, export_service_envvars(service_envvars, service))


async def orchestrate(services, environment, service_envvars):
    experiment_start_time = time()
    prometheus_port = environment.get(PROMETHEUS_PORT, DEFAULT_PROMETHEUS_PORT)

    try:
        processes = {}
        completed_processes = {}
        for service in services:
            new_proc = await run_benchmark(service, export_service_envvars(service_envvars, service))
            processes[service] = {
                "service": service, "process": new_proc, "start_time": time(),
                "environment": service_envvars[service] if service in service_envvars else {}
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
                        collect_all_service_metrics(processes[finished_service_name], DEFAULT_PROMETHEUS_HOSTNAME, prometheus_port)
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

        stop_prometheus_server()


def orchestrate_deployment(deployment_config, services, service_envvars, environment):

    compose_filename = environment.get(DEPLOYMENT_COMPOSE_FILE)
    prometheus_port = environment.get(PROMETHEUS_PORT, DEFAULT_PROMETHEUS_PORT)
    prometheus_hostname = f'{PROMETHEUS_SERVER_NAME}.ukwest.azurecontainer.io'

    subscription_id = deployment_config.get(AZURE_SUBSCRIPTION_ID)
    container_registry = deployment_config.get(AZURE_CONTAINER_REGISTRY)
    container_registry_username = deployment_config.get(AZURE_CONTAINER_REGISTRY_USERNAME)
    container_registry_password = deployment_config.get(AZURE_CONTAINER_REGISTRY_PASSWORD)
    storage_account_name = deployment_config.get(AZURE_STORAGE_ACCOUNT_NAME)
    storage_account_key = deployment_config.get(AZURE_STORAGE_ACCOUNT_KEY)
    storage_share_name = deployment_config.get(AZURE_FILE_SHARE_NAME)
    aci_context = deployment_config.get(AZURE_DOCKER_ACI_CONTEXT)

    print("Authenticating...")
    container_instance_client = log_into_container_instances_management(subscription_id)
    res_client = log_into_resource_management(subscription_id)
    resource_group = res_client.resource_groups.get(deployment_config.get(AZURE_RESOURCE_GROUP))

    ensure_docker_context(subscription_id, resource_group.name, context="default", context_is_aci=False)

    # Push Prometheus' image to registry
    prometheus_image = f"{container_registry}.azurecr.io/{PROMETHEUS_SERVER_NAME}:latest"
    build_and_push_single_docker_image(
        prometheus_image, PROMETHEUS_SERVER_NAME, PROMETHEUS_FOLDER)

    container_factory = AzureContainerInstanceFactory(
        container_instance_client=container_instance_client,
        resource_group=resource_group,
        container_registry=container_registry,
        container_registry_username=container_registry_username,
        container_registry_password=container_registry_password,
        storage_name=storage_account_name,
        storage_key=storage_account_key,
        file_share_name=storage_share_name,
    )

    prometheus_ip = container_factory.deploy_single_container(
        container_group_name=PROMETHEUS_SERVER_NAME,
        container_image_name=prometheus_image,
        ports=[int(environment.get(PROMETHEUS_PORT, DEFAULT_PROMETHEUS_PORT))],
    )
    if prometheus_ip is None:
        print("Error obtaining container IP. Is the group running?", file=sys.stderr)

    delete_storage_finish_files(
        storage_account_name, storage_account_key, storage_share_name, services)

    cmd_run("docker login azure", shell=True, check=True)
    processes = {}
    finished_processes = {}
    try:
        for service in services:
            service_path = f'{MICROSERVICES_PATH}{service}'

            build_and_push_docker_compose(
                service, service_path, compose_filename,
                export_service_and_deployment_envvars(service_envvars, service, deployment_config))

        ensure_docker_context(subscription_id, resource_group.name, aci_context,  context_is_aci=True)

        for service in services:
            service_path = f'{MICROSERVICES_PATH}{service}'
            deploy_docker_compose(
                service, compose_filename, cwd=service_path,
                env=export_service_and_deployment_envvars(service_envvars, service, deployment_config))

            processes[service] = {
                "service": service, "start_time": time(),
                "environment": service_envvars[service] if service in service_envvars else {}
            }

        experiment_start_time = time()
        while True:

            duration = datetime.fromtimestamp(time() - experiment_start_time)
            print("Experiment running:", duration.strftime('%H:%M:%S'), end='\r')

            finish_files = poll_storage_finish_files(storage_account_name, storage_account_key, storage_share_name)
            for finished_file in finish_files:
                finished_service = finished_file.split('.')[0]
                if finished_service in processes:
                    print(f"\nService {finished_service} finished at {time()}")
                    processes[finished_service]['end_time'] = time()
                    collect_all_service_metrics(processes[finished_service], prometheus_hostname, prometheus_port)
                    finished_processes[finished_service] = processes.pop(finished_service)

                    collect_compose_logs(finished_service, f"{MICROSERVICES_PATH}{finished_service}")
                    stop_compose_process(
                        finished_service, compose_filename, f'{MICROSERVICES_PATH}{finished_service}',
                        export_service_and_deployment_envvars(service_envvars, service, deployment_config))

            if len(processes) == 0:
                print("Experiment finished")
                return

            sleep(5)

    except KeyboardInterrupt:
        print("\nExperiment cancelled manually. Collecting logs and stopping services...")
        for service_name in processes.keys():
            collect_compose_logs(service_name, f"{MICROSERVICES_PATH}{finished_service}")
            stop_compose_process(
                compose_filename, f'{MICROSERVICES_PATH}{service_name}',
                export_service_and_deployment_envvars(service_envvars, service_name, deployment_config))

    except (MetricCollectionError) as e:
        print(e)
        print("Error collecting data. Collecting logs and stopping services...")
        for service_name in processes.keys():
            collect_compose_logs(service_name, f"{MICROSERVICES_PATH}{finished_service}")
            stop_compose_process(
                compose_filename, f'{MICROSERVICES_PATH}{service_name}',
                export_service_and_deployment_envvars(service_envvars, service_name, deployment_config))

    finally:
        container_factory.delete_container_group(PROMETHEUS_SERVER_NAME)


async def main():
    config = parse_and_validate_config()
    services = list(config['services'].keys())
    service_envvars = parse_service_envvars(config)
    environment = parse_environment(config)
    is_deployment = environment.get(DEPLOYMENT, None) == 'True'
    prepare_prometheus_configuration(service_envvars, is_deployment)

    if is_deployment:
        deployment_config = parse_azure(config)
        try:
            orchestrate_deployment(deployment_config, services, service_envvars, environment)
        except CalledProcessError as err:
            print("Deployment command failed with error:\n", err.stderr.decode("utf-8"))
            return

    else:
        run_prometheus_server()
        print(run_auxiliary_script('remove_finished_volumes.py', ' '.join(services), True).stdout)
        await orchestrate(services, environment, service_envvars)

if __name__ == "__main__":
    run(main())
