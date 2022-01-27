from asyncio.subprocess import PIPE
from azure.identity import DefaultAzureCredential
from azure.mgmt.containerinstance import ContainerInstanceManagementClient
from azure.mgmt.containerinstance.models import (
    ContainerGroup, Container, ContainerGroupNetworkProtocol, VolumeMount,
    ContainerPort, IpAddress, Port, ResourceRequests, ResourceRequirements,
    OperatingSystemTypes, ImageRegistryCredential, Volume, AzureFileVolume,
    ContainerGroupIpAddressType)
from azure.mgmt.resource import ResourceManagementClient
from subprocess import run as cmd_run
from os import makedirs, path

from azure.storage.file import (
    FileService
)

from config_parser import is_string_dockerfile_envvar, parse_variables


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
    if not path.exists(file_directories):
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

    docker_build_proc = cmd_run(f"docker build -t {full_image_name} {path}",
                                shell=True, check=True, stdout=PIPE, stderr=PIPE)

    docker_push_proc = cmd_run(f"docker push {full_image_name}",
                               shell=True, check=True, stdout=PIPE, stderr=PIPE)

    for process, filename in [
        (docker_build_proc, f'build_{service_name}'),
        (docker_push_proc, f'push_{service_name}')
    ]:
        capture_process_log(process, f'{logs_location}{filename}.log', is_error_log=False)
        capture_process_log(process, f'{logs_location}{filename}.error', is_error_log=True)

    return full_image_name


def build_and_push_multicontainer_subservice(
        full_image_name, service_name, container_service, path, env, logs_location):

    print(f"Building {full_image_name}...")
    docker_build_proc = cmd_run(
        f"docker build -t {full_image_name} {path}/{container_service}",
        shell=True, check=True, stdout=PIPE, stderr=PIPE)
    capture_process_log(docker_build_proc, f'{logs_location}build_{service_name}.log', is_error_log=False)
    capture_process_log(docker_build_proc, f'{logs_location}build_{service_name}.error', is_error_log=True)

    print(f"Pushing {full_image_name}...")
    docker_push_proc = cmd_run(
        f"docker push {full_image_name}", shell=True, check=True,
        stdout=PIPE, stderr=PIPE, cwd=path, env=env)
    capture_process_log(docker_push_proc, f'{logs_location}push_{service_name}.log', is_error_log=False)
    capture_process_log(docker_push_proc, f'{logs_location}push_{service_name}.error', is_error_log=True)


def build_and_push_multi_container_image(
        container_registry, full_image_name, service_name,
        path, env, docker_compose_config, logs_location='./logs/deployment/'):

    container_services = list(docker_compose_config.get('services').keys())

    for container_service in container_services:
        full_image_name = f"{container_registry}.azurecr.io/{service_name}-{container_service}:latest"

        build_and_push_multicontainer_subservice(
            full_image_name, service_name, container_service, path, env, logs_location)


def build_and_push_docker_compose_images(
        container_registry, container_registry_username,
        container_registry_password, service_name,
        path, tag='latest', logs_location='./logs/deployment/'):
    full_image_name = f"{container_registry}.azurecr.io/{service_name}:{tag}"

    docker_build_proc = cmd_run(f"docker build -t {full_image_name} {path}",
                                shell=True, check=True, stdout=PIPE, stderr=PIPE)

    auth_proc = cmd_run(
        f"echo '{container_registry_password}' | docker login {container_registry}.azurecr.io --username={container_registry_username} --password-stdin",
        shell=True, check=True, stdout=PIPE, stderr=PIPE)

    docker_push_proc = cmd_run(f"docker push {full_image_name}",
                               shell=True, check=True, stdout=PIPE, stderr=PIPE)

    for process, filename in [
        (docker_build_proc, f'build_{service_name}'),
        (auth_proc, f'auth_{container_registry}'),
        (docker_push_proc, f'push_{service_name}')
    ]:
        capture_process_log(process, f'{logs_location}{filename}.log', is_error_log=False)
        capture_process_log(process, f'{logs_location}{filename}.error', is_error_log=True)

    return full_image_name


def delete_remote_storage_service_files(
        storage_account_name, storage_account_key, share_name, services):
    file_service = FileService(
        account_name=storage_account_name, account_key=storage_account_key)
    current_filenames = [file.name for file in list(
        file_service.list_directories_and_files(share_name))]
    for service in services:
        finish_file_name = f'{service}.finish'

        if finish_file_name in current_filenames:
            print(f"Deleting {service} finish file...")
            file_service.delete_file(share_name, None, finish_file_name)


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
