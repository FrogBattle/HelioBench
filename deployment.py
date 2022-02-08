from asyncio.subprocess import PIPE
from time import time
from azure.identity import DefaultAzureCredential
from azure.mgmt.containerinstance import ContainerInstanceManagementClient
from azure.mgmt.containerinstance.models import (
    ContainerGroup, Container, ContainerGroupNetworkProtocol, VolumeMount,
    ContainerPort, IpAddress, Port, ResourceRequests, ResourceRequirements,
    OperatingSystemTypes, ImageRegistryCredential, Volume, AzureFileVolume,
    ContainerGroupIpAddressType)
from azure.mgmt.resource import ResourceManagementClient
from subprocess import CalledProcessError, run as cmd_run
from os import makedirs, path as os_path

from azure.storage.file import (
    FileService
)

from config_parser import is_string_dockerfile_envvar, parse_variables


class HandledCalledProcessError(Exception):
    def __init__(
            self, command, logs_path,
            message="An error occurred while running a deployment command '{}'. See logs in '{}'."):
        self.command = command
        self.logs_path = logs_path
        self.message = message.format(command, logs_path)
        super().__init__(self.message)


def log_into_container_instances_management(subscription_id):
    cred = DefaultAzureCredential()
    client = ContainerInstanceManagementClient(cred, subscription_id)
    return client


def log_into_resource_management(subscription_id):
    cred = DefaultAzureCredential()
    client = ResourceManagementClient(cred, subscription_id)
    return client


def capture_process_log(process, filepath, is_error_log=False):
    file_directories = "/".join(filepath.split("/")[:-1])
    if not os_path.exists(file_directories):
        makedirs(file_directories)

    with open(filepath, 'wb+') as file:
        process_lines = process.stdout if not is_error_log else process.stderr
        file.write(process_lines)


def docker_login_to_container_registry(
        container_registry, container_registry_username,
        container_registry_password, logs_location='./logs/deployment/'):
    auth_proc = cmd_run(
        f"echo '{container_registry_password}' | docker login {container_registry}.azurecr.io --username={container_registry_username} --password-stdin",
        shell=True, check=True, stdout=PIPE, stderr=PIPE)

    log_filename = f'auth_{container_registry}'
    capture_process_log(auth_proc, f'{logs_location}{log_filename}.log', is_error_log=False)
    capture_process_log(auth_proc, f'{logs_location}{log_filename}.error', is_error_log=True)


def build_and_push_single_docker_image(
        full_image_name, service_name,
        path, logs_location='./logs/deployment/'):

    docker_build_proc = None
    docker_push_proc = None
    build_path = f'{logs_location}{service_name}/build'
    push_path = f'{logs_location}{service_name}/push'

    build_command = f"docker build -t {full_image_name} {path}"
    try:
        docker_build_proc = cmd_run(build_command, shell=True, check=True, stdout=PIPE, stderr=PIPE)
    except CalledProcessError as err:
        capture_process_log(err, f'{build_path}.error', is_error_log=True)
        raise HandledCalledProcessError(build_command, f'{build_path}.error')

    push_command = f"docker push {full_image_name}"
    try:
        docker_push_proc = cmd_run(push_command, shell=True, check=True, stdout=PIPE, stderr=PIPE)
    except CalledProcessError as err:
        capture_process_log(err, f'{push_path}.error', is_error_log=True)
        raise HandledCalledProcessError(push_command, f'{push_path}.error')

    if docker_build_proc is not None and docker_push_proc is not None:
        for process, filepath in [
            (docker_build_proc, build_path),
            (docker_push_proc, push_path)
        ]:
            capture_process_log(process, f'{filepath}.log', is_error_log=False)
            capture_process_log(process, f'{filepath}.error', is_error_log=True)

    return full_image_name


# def build_and_push_multicontainer_subservice(
#         full_image_name, service_name, container_service, path, env, logs_location):

#     docker_build_proc = None
#     docker_push_proc = None
#     build_path = f'{logs_location}{service_name}/build'
#     push_path = f'{logs_location}{service_name}/push'

#     build_command = f"docker build -t {full_image_name} {path}/{container_service}"
#     try:
#         print(f"Building {full_image_name}...")
#         docker_build_proc = cmd_run(build_command, shell=True, check=True, stdout=PIPE, stderr=PIPE, env=env)

#     except CalledProcessError as err:
#         capture_process_log(err, f'{build_path}.error', is_error_log=True)
#         raise HandledCalledProcessError(build_command, f'{build_path}.error')

#     if docker_build_proc is not None:
#         capture_process_log(docker_build_proc, f'{build_path}.log', is_error_log=False)
#         capture_process_log(docker_build_proc, f'{build_path}.error', is_error_log=True)

#     push_command = f"docker push {full_image_name}"
#     try:
#         print(f"Pushing {full_image_name}...")
#         docker_push_proc = cmd_run(push_command, shell=True, check=True,
#                                    stdout=PIPE, stderr=PIPE, cwd=path, env=env)
#     except CalledProcessError as err:
#         capture_process_log(err, f'{push_path}.error', is_error_log=True)
#         raise HandledCalledProcessError(push_command, f'{push_path}.error')

#     if docker_push_proc is not None:
#         capture_process_log(docker_push_proc, f'{push_path}.log', is_error_log=False)
#         capture_process_log(docker_push_proc, f'{push_path}.error', is_error_log=True)


# def build_and_push_multi_container_image(
#         container_registry, full_image_name, service_name,
#         path, env, docker_compose_config, logs_location='./logs/deployment/'):

#     container_services = list(docker_compose_config.get('services').keys())

#     for container_service in container_services:
#         full_image_name = f"{container_registry}.azurecr.io/{service_name}-{container_service}:latest"

#         build_and_push_multicontainer_subservice(
#             full_image_name, service_name, container_service, path, env, logs_location)


# def build_and_push_docker_compose_images(
#         container_registry, container_registry_username,
#         container_registry_password, service_name,
#         path, tag='latest', logs_location='./logs/deployment/'):
#     full_image_name = f"{container_registry}.azurecr.io/{service_name}:{tag}"

#     docker_build_proc = cmd_run(f"docker build -t {full_image_name} {path}",
#                                 shell=True, check=True, stdout=PIPE, stderr=PIPE)

#     auth_proc = cmd_run(
#         f"echo '{container_registry_password}' | docker login {container_registry}.azurecr.io --username={container_registry_username} --password-stdin",
#         shell=True, check=True, stdout=PIPE, stderr=PIPE)

#     docker_push_proc = cmd_run(f"docker push {full_image_name}",
#                                shell=True, check=True, stdout=PIPE, stderr=PIPE)

#     for process, filename in [
#         (docker_build_proc, f'build_{service_name}'),
#         (auth_proc, f'auth_{container_registry}'),
#         (docker_push_proc, f'push_{service_name}')
#     ]:
#         capture_process_log(process, f'{logs_location}{filename}.log', is_error_log=False)
#         capture_process_log(process, f'{logs_location}{filename}.error', is_error_log=True)

#     return full_image_name


def build_and_push_docker_compose(
        service_name, path, compose_filename, env, logs_location='./logs/deployment/'):

    print(f"Building and pushing {service_name}")
    docker_build_proc, docker_push_proc = None, None
    build_filename, push_filename = f'{logs_location}{service_name}/build', f'{logs_location}{service_name}/push'

    build_command = f"docker-compose -f {compose_filename} build"
    try:
        docker_build_proc = cmd_run(
            build_command, shell=True, check=True, capture_output=True, cwd=path, env=env)
    except CalledProcessError as err:
        capture_process_log(err, f'{build_filename}.error', is_error_log=True)
        raise HandledCalledProcessError(build_command, f'{build_filename}.error')

    push_command = f"docker-compose -f {compose_filename} push"
    try:
        docker_push_proc = cmd_run(
            push_command, shell=True, check=True, stdout=PIPE, stderr=PIPE, cwd=path, env=env)
    except CalledProcessError as err:
        capture_process_log(err, f'{push_filename}.error', is_error_log=True)
        raise HandledCalledProcessError(push_command, f'{push_filename}.error')

    for process, filename in [
        (docker_build_proc, build_filename),
        (docker_push_proc, push_filename)
    ]:
        if process is not None:
            capture_process_log(process, f'{filename}.log', is_error_log=False)
            capture_process_log(process, f'{filename}.error', is_error_log=True)


def deploy_docker_compose(service, compose_filename, cwd, env):
    print(f"Deploying {service}. This may take a while...")
    cmd_run(f"docker compose -f {compose_filename} up", shell=True, check=True, cwd=cwd, env=env)
    print(f"Successfully deployed {service} at {time()}")


def stop_compose_process(service, compose_filename, cwd, env):
    print(f"Stopping service {service}...")
    cmd_run(
        f"docker compose -f {compose_filename} down",
        shell=True, check=True, capture_output=True, cwd=cwd, env=env)


def collect_compose_logs(service, cwd, logs_folder='./logs/deployment/'):
    sub_services = cmd_run('docker ps -q', shell=True, cwd=cwd, capture_output=True, text=True).stdout.split('\n')
    for sub_service in sub_services:
        if sub_service.startswith(service):
            print(f"Collecting logs for {sub_service}...")
            log_process = cmd_run(f"docker logs {sub_service}", shell=True, check=True, capture_output=True, cwd=cwd)

            service_dir = f"{logs_folder}{sub_service.replace('_', '/')}"
            capture_process_log(log_process, f'{service_dir}/log.log', is_error_log=False)
            capture_process_log(log_process, f'{service_dir}/log.error', is_error_log=True)


def delete_storage_finish_files(
        storage_account_name, storage_account_key, share_name, services):
    file_service = FileService(account_name=storage_account_name, account_key=storage_account_key)
    current_filenames = [file.name for file in list(file_service.list_directories_and_files(share_name))]
    for service in services:
        finish_file_name = f'{service}.finish'

        if finish_file_name in current_filenames:
            print(f"Deleting {service} finish file...")
            file_service.delete_file(share_name, None, finish_file_name)


def poll_storage_finish_files(storage_account_name, storage_account_key, share_name):
    file_service = FileService(account_name=storage_account_name, account_key=storage_account_key)
    current_filenames = [file.name for file in list(file_service.list_directories_and_files(share_name))]
    return current_filenames


def ensure_docker_context(subscription_id, resource_group, context="default", context_is_aci=True):
    try:
        cmd_run(f"docker context use {context}", check=True, shell=True, capture_output=True)
    except CalledProcessError as err:
        if f'context "{context}": not found' not in err.stderr.decode("utf-8"):
            raise err

        print(f"Did not find Docker context {context}, creating it now...")
        if context_is_aci:
            cmd_run(f"docker context create aci {context} --subscription-id={subscription_id}"
                    f" --resource-group={resource_group}",
                    check=True, shell=True)
        else:
            cmd_run(f"docker context create {context}", check=True, shell=True)
        cmd_run(f"docker context use {context}", check=True, shell=True)


def collect_logs_and_stop_processes(processes, compose_filename):
    for service_name, service_details in processes.items():
        collect_compose_logs(service_name, service_details['service_path'])
        stop_compose_process(service_name, compose_filename, service_details['service_path'],
                             service_details['environment'])


class AzureContainerInstanceFactory:
    def __init__(self,
                 container_instance_client,
                 resource_group,
                 container_registry,
                 container_registry_username,
                 container_registry_password,
                 storage_name,
                 storage_key,
                 file_share_name):

        self.container_instance_client = container_instance_client
        self.resource_group = resource_group

        self.image_registry_credentials = [ImageRegistryCredential(
            server=f'{container_registry}.azurecr.io',
            username=container_registry_username,
            password=container_registry_password)]

        self.volume_mounts = [VolumeMount(
            name=storage_name,
            mount_path='/home/experiment',
            read_only=False)]

        self.volumes = [Volume(
            name=storage_name,
            azure_file=AzureFileVolume(
                share_name=file_share_name,
                read_only=False,
                storage_account_name=storage_name,
                storage_account_key=storage_key))]

    def create_azure_containers(self, container_registry, service_name, docker_compose_config, service_envvars):
        # TODO: Make this function read the experiment file for any resource requirements.
        container_services = list(docker_compose_config.get('services').keys())
        containers = []
        group_ports = []

        for container_service in container_services:
            full_image_name = f"{container_registry}.azurecr.io/{service_name}-{container_service}:latest"
            service_docker_config = docker_compose_config.get('services').get(container_service)

            container_resource_requests = ResourceRequests(memory_in_gb=1, cpu=1.0)
            container_resource_requirements = ResourceRequirements(requests=container_resource_requests)

            container_ports = []
            service_ports = service_docker_config.get('ports', None)

            # TODO: Improve this part - massive complexity
            if service_ports is not None:
                parsed_service_ports = parse_variables(service_ports, delimiter=':')
                if len(parsed_service_ports) != 0:
                    for port in parsed_service_ports.values():
                        if port.isdigit():
                            container_ports.append(int(port))
                        else:
                            is_envvar, envvar_string = is_string_dockerfile_envvar(port)
                            if (is_envvar and service_envvars.get(service_name, None) is not None and
                                    service_envvars.get(service_name).get(envvar_string, None) is not None):
                                container_ports.append(int(service_envvars.get(service_name).get(envvar_string)))

            group_ports.extend(container_ports)
            containers.append(Container(
                name=f'{service_name}-{container_service}',
                image=full_image_name,
                resources=container_resource_requirements,
                ports=[ContainerPort(port=port) for port in container_ports],
                volume_mounts=self.volume_mounts))

        return containers, group_ports

    def deploy_single_container(self, container_group_name, container_image_name, ports, done_callback=lambda _: None):
        print(f"Deploying {container_group_name}...")

        container_instance_client = self.container_instance_client
        resource_group = self.resource_group

        # Configure the container
        container_resource_requests = ResourceRequests(memory_in_gb=1, cpu=1.0)
        container_resource_requirements = ResourceRequirements(requests=container_resource_requests)

        container = Container(name=container_group_name,
                              image=container_image_name,
                              resources=container_resource_requirements,
                              ports=[ContainerPort(port=port) for port in ports],
                              volume_mounts=self.volume_mounts)

        # Configure the container group
        ports = [Port(protocol=ContainerGroupNetworkProtocol.tcp, port=port) for port in ports]
        group_ip_address = IpAddress(ports=ports, dns_name_label=container_group_name,
                                     type=ContainerGroupIpAddressType.PUBLIC)

        group = ContainerGroup(location=resource_group.location,
                               containers=[container],
                               os_type=OperatingSystemTypes.linux,
                               ip_address=group_ip_address,
                               image_registry_credentials=self.image_registry_credentials,
                               volumes=self.volumes)

        # Create the container group
        container_instance_client.container_groups.begin_create_or_update(
            resource_group.name, container_group_name, group).wait()

        # Get the created container group
        container_group = container_instance_client.container_groups.get(
            resource_group.name, container_group_name)

        print(f"Successfully deployed {container_group_name}")
        return container_group.ip_address.ip

        # print("Once DNS has propagated, container group '{0}' will be reachable at"
        #     " http://{1}".format(
        # container_group_name, container_group.ip_address.fqdn))

    def create_container_group_multi(self, container_group_name, containers, ports):

        container_instance_client = self.container_instance_client
        resource_group = self.resource_group

        print("Deploying container group '{0}'...".format(container_group_name))

        # Configure the container group
        ports = [Port(protocol=ContainerGroupNetworkProtocol.tcp, port=port) for port in ports]
        group_ip_address = IpAddress(
            ports=ports, dns_name_label=container_group_name, type=ContainerGroupIpAddressType.PUBLIC)
        group = ContainerGroup(location=resource_group.location,
                               containers=containers,
                               os_type=OperatingSystemTypes.linux,
                               ip_address=group_ip_address,
                               image_registry_credentials=self.image_registry_credentials,
                               volumes=self.volumes)

        # Create the container group
        operation_poller = container_instance_client.container_groups.begin_create_or_update(
            resource_group_name=resource_group.name,
            container_group_name=container_group_name,
            container_group=group)

        # If poller is already done, we trigger a manual restart to pull newest images
        if operation_poller.done():
            operation_poller = container_instance_client.container_groups.begin_restart(
                resource_group_name=resource_group.name,
                container_group_name=container_group_name,
            ).wait()

        else:
            operation_poller.wait()

        # Get the created container group
        container_group = container_instance_client.container_groups.get(
            resource_group.name, container_group_name)

        print(f"Successfully deployed group {container_group_name}")
        # print("Deployd", isinstance(container_group, ContainerGroup), container_group)
        # print("instance view state", container_group.instance_view.state)
        return container_group.ip_address.ip

    def delete_container_group(self, container_group_name):
        container_instance_client = self.container_instance_client
        resource_group = self.resource_group

        container_instance_client.container_groups.begin_delete(
            resource_group_name=resource_group.name,
            container_group_name=container_group_name,
        ).wait()

        print(f"Stopped container group {container_group_name}")
