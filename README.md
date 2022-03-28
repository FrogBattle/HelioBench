# HelioBench
HelioBench is an automatatically orchestrated microservice benchmarking suite. It allows for the orchestrated run of benchmark services in local Docker containers or in the cloud.

This document outlines the user documentation for the project. It outlines important details regarding the project, how to run it, and finally, a step-by-step guide on how to integrate a new benchmark.


## Project Structure
The HelioBench repository consists of several types of files, based on their corresponding role in the project. The main files and folders are outlined in the table below:
| File Domain       | Included file/folder | Rationale                                                                                                                              |
|-------------------|----------------------|----------------------------------------------------------------------------------------------------------------------------------------|
| Orchestrator      | `*.py`               | Python files specify relevant orchestrator modules.                                                                                    |
|                   | `scripts/`           | Includes auxiliary scripts ran while performing local experiments.                                                                     |
|                   | `orchestrator.py`    | The entrypoint into the HelioBench orchestrator.                                                                                       |
| Benchmarks        | `microservices/`     | This folder contains the benchmarking suite. It includes a folder for each benchmarked service with relevant benchmark configurations. |
| Utilities         | `azure_utilities/`   | Includes Azure CLI scripts for the easy creation of Azure entities required by remote HelioBench experiments.                          |
|                   | `examples/`          | Includes example local and remote experiment configuration.                                                                            |
|                   | `requirements.txt`   | Python library requirements, needed for running HelioBench.                                                                            |
|                   | `experiment.yml`     | The main experiment configuration file, required for running HelioBench experiments.                                                   |
| Development tools | `.vscode/`           | The folder includes IDE configuration used throughout the development of HelioBench.                                                   |
|                   | `.flake8`            | A Flake configuration file used while developing HelioBench.                                                                           |


## Available Benchmarks
The `microservices/` folder contains all services, benchmarked in HelioBench by default. Each benchmark is specified by a `docker-compose` file for local experiments and a `deployment.yml` file for remote experiments. Further, the folder contains the specification required for Prometheus - the monitoring service used by HelioBench. The following list describes all available benchmarks:
- `alexnet` - This is a Python service which performs training of an image recognition CNN model, similar to AlexNet, over the CIFAR10 dataset.
- `alexnet-inference` - This is a Python service, which performs inference of the Keras' CIFAR10 dataset over an 18-layer pre-trained Resnet model from MXNet. The input dataset is randomised in order to avoid cache locality.
- `go-api` - This benchmark consists of a simple Web API service written in Go and a corresponding Locust workload service, performing GET, POST, and DELETE HTTP requests.
- `memcached` - This benchmark includes a Memcached service, ran thought an official Docker container, benchmarked by a client running memaslap, a lightweight and configurable load generator tool for memcached services
- `nginx-web` - This benchmark includes an NGINX web server which exposes several web pages of different sizes. Its workload is performed by Apache's web server benchmarking tool `ab`.
- `text-analysis` - This benchmark runs a simple Python experiment over a small load. This is an ***example benchmark*** as its workload is small and it finishes very quickly. It can be used to verify the successful completion of experiments.


## Experiment Configuration
The `experiment.yml` file specifies the configurations of an experiment to be run. The experiment file has the following sections:
- `services`. This section concerns service configurations to be run. Much like `docker-compose` files, it lists services by **specifying their name** as in the `./microservices` folder. Within each service configuration, environment variables can be specified. They are exported into processes which build and create Docker containers. As such, they can be used within container specifications. For example, `GO_API_WEB_PORT` is specified under the `go-api` clause. It is then used within the `deployment.yml` file to map the same port specified within the `experiment.yml` file. 
- `environment`. This section specifies experiment-wide environment settings. For example, the central Prometheus service port or whether a deployed experiment is perforemed. These variables are all exported into each service as well. For a full description of all possible settings see below.
- `azure`. This section concerns settings relevant to cloud deployed services via Azure ACI. See all available settings below.

Example experiment specifications for both local and remote experiments could be found in the `./examples` folder in the project root directory. Further, the default project `./experiment.yml` file contains relevant settings in the form of comments.


## Benchmark Configuration
Each individual benchmark includes relevant variables which change its operation. All setting specified in the `variables` section of the `experiment.yml` file for a given benchmark _will be exported into the process running the benchmark_. Therefore, adding a new variable in the experiment configuration makes it available within its Docker context, which, in turn, could make it available to the process runtime if needed. The table below describes the required environment variables for all benchmarks. Similar variables are available in other benchmarks. They can all be seen in each benchmark's corresponding `docker-compose` or `deployment.yml` files.

| Setting                    | Rationale                                                                                                                                |
|----------------------------|------------------------------------------------------------------------------------------------------------------------------------------|
| `PROMETHEUS_TARGET_PORT`   | This specifies the port on which the Prometheus Node service will export metrics for the benchmark.                                      |
| `EXPERIMENT_WORKLOAD`      | This setting is **automatically** exported for each benchmark and contains its name as specified in the `microservices/` folder.         |
| `AZURE_CONTAINER_REGISTRY` | This setting is **required** for deployed experiments as it specifies the image destination of the benchmark.                            |
| `DOMAIN_NAME`              | The variable is **required** for deployed experiments as it specifies the benchmark hostname.                                            |
| `XXXX_NUM_CPUS`            | The variable is **required** for deployed experiments. It specifies the number of CPUs (in Azure millicores) to be given to the service. |
| `XXXX_NUM_RAM`             | The variable is **required** for deployed experiments. It specifies the Memory to be given to the service.                               |
| `XXXX_CPU_LIMIT`           | The variable is **required** for deployed experiments. It specifies the limit of CPUs for the ACI.                                       |
| `XXXX_RAM_LIMIT`           | The variable is **required** for deployed experiments. It specifies the limit of Memory for the ACI.                                     |

**Note**: The `EXPERIMENT_WORKLOAD` environment variable is automatically exported to each benchmark and contains its name, eg: `go-api` for the Go API benchmark.


## Prometheus
Prometheus is the monitoring framework used by HelioBench. In order to carry out experiments and monitor benchmark performance, a Prometheus instance **must** be put up. The Prometheus configuration artefacts are stored in the `./microservices/prometheus/` folder. The folder **must** contain a `prometheus.yml` file which will be used as a basis for the dynamically computed Prometheus configuration. An example file is provided within the folder to serve as a basis for newcomers.

**Note**: This file is **partially recomputed** during runtime. The `targets` list is computed to reflect the benchmarks specified within `experiment.yml`. However, other specifications of the file are persisted and could be manually changed.

## Experiment Environment
The `environment` section of the experiment configuration file contains settings which change the way HelioBench operates in general. Below are all possible settings:
| Environment Setting       | Description                                                               | Required?                               |
|---------------------------|---------------------------------------------------------------------------|-----------------------------------------|
| `PROMETHEUS_PORT`         | The Azure subscription all entities are created within.                   | Optional. Defaults to `9090`.           |
| `STOP_PROMETHEUS`         | The Azure resource group of all entities created for experiment purposes. | Optional. Defaults to `True`.           |
| `DEPLOYMENT`              | The Azure CR where to publish and pull Docker images for experiments.     | Optional. Defaults to `False`.          |
| `DEPLOYMENT_COMPOSE_FILE` | ACR username for authentication and creation of container instances.      | Optional. Defaults to `deployment.yml`. |
  
## Running HelioBench
### Virtual Environment
Before running the project, you need to make sure that you have created a virtual environment. Follow the steps below to create one and activate it:
1. Make sure you have at least **Python 3.9** installed. 
2. Create a virtual environment using `python3 -m venv ./venv` at the project root. 
3. Install all project requirements by running `pip3 install -r requirements.txt` from the project root directory.
4. Activate the virtual environment running `source ./venv/bin/activate` for UNIX users or `venv\Scripts\activate.bat` for Windows users.

### Local experiments 
The main configuration file HelioBench uses is `experiment.yml`. In order to run local experiments, make sure that `DEPLOYMENT=False` in the `environment` section is set or the variable is commented out.

Further, a Docker network must be created in order to run local experiments. This could be done with the following command
```bash
docker network create -d bridge HelioBench-network # Or any other network name
```
Alternatively, you could execute the `./create_volume_and_network.sh` bash script to automate this. By default, all HelioBench workloads work with `HelioBench-network`-named network and a `HelioBench`-named volume. This could be abstracted out and automated. See issue [9](https://github.com/FrogBattle/HelioBench/issues/9) for more details.

To run an experiment, execute `python3 orchestrator.py`. This is the main command for running HelioBench. The default configuration of HelioBench runs a Go API benchmark for several minutes.

### Cloud Experiments - Azure
Additional configuration required in `experiment.yml` includes setting `DEPLOYMENT=True` in the `environment` section and popualting all relevant configuration regarding Azure entities.

**Note**: If you need to create all Azure entities for running HelioBench, the automated scripts in `./azure_utilities` could help you. Set configurations within each script or environment variables and execute them by running `./{script_name}.sh` to create relevant entities.

The configurations available within `experiment.yml` relevant to Azure include:
| Variable Name                       | Description                                                                                                                  | Required? |
|-------------------------------------|------------------------------------------------------------------------------------------------------------------------------|-----------|
| `AZURE_SUBSCRIPTION_ID`             | The Azure subscription all entities are created within.                                                                      | Required. |
| `AZURE_RESOURCE_GROUP`              | The Azure resource group of all entities created for experiment purposes.                                                    | Required. |
| `AZURE_CONTAINER_REGISTRY`          | The Azure CR where to publish and pull Docker images for experiments.                                                        | Required. |
| `AZURE_CONTAINER_REGISTRY_USERNAME` | ACR username for authentication and creation of container instances.                                                         | Required. |
| `AZURE_CONTAINER_REGISTRY_PASSWORD` | ACR password for authentication and creation of container instances.                                                         | Required. |
| `AZURE_STORAGE_ACCOUNT_NAME`        | Azure Storage name for the creation and polling of finish files.                                                             | Required. |
| `AZURE_STORAGE_ACCOUNT_KEY`         | Azure Storage key for the creation and polling of finish files.                                                              | Required. |
| `AZURE_FILE_SHARE_NAME`             | Azure File Share - the actual FS shared between services where files are created/deleted.                                    | Required. |
| `AZURE_DOCKER_ACI_CONTEXT`          | The Docker context required by the Docker compose integration to work with Azure ACIs.                                       | Required. |

After setting all required configurations, HelioBench should run successfully by running `python3 orchestrator.py` as usual.

# Adding a New Benchmark
On condition that HelioBench gains interest, this guide may be helpful in extending the benchmarking suite. The following subsections outline step-by-step suggestions on integrating a new benchmark into the suite.

## Boilerplate code
There are several pieces of benchmark boilerplate configuration which need to be included within each benchmark for it to be available for HelioBench orchestration:
- Node exporter process to expose microservice metrics.
- An exposed port, over which the Prometheus server would scrape configuration.
- Connection to a shared storage for the coordination of finish files.
- Deployment details on condition that remote experiments should be supported for the benchmark.

## Local Experiment Benchmark Integration Guide
### 1. Create a `docker-compose` benchmark specification
HelioBench works with local benchmarks via `docker-compose` commands. Therefore, any benchmark needs to be Dockerised and include a `docker-compose` specification. This is true even if the benchmark contains one service. See `alexnet` and `alexnet-inference` for such examples.

In order to successfully perform local orchestration, the Docker compose specification must include a **network** and **storage** configuration for the Prometheus service to communicate successfully with the benchmark and the orchestrator to know when the service has finished executing respectively.

The network configuration must include a **predefined Docker network** which has to be specified when building both the Prometheus service and within the Docker compose specification of any benchmark. For example, the Prometheus service run specification specifies the `HelioBench-network` network. Further, the `alexnet` Docker compose specifies the same network. Within the compose file, the network should be specified **for each individual service as well**. See the current benchmark compose files for examples of this. See [this](https://docs.docker.com/engine/reference/commandline/network_create/) for information on how to create a pre-defined Docker network.

The volume configuration is similar. It has to be specified within each benchmark compose file and within the individual service specification in the compose file. Further, the volume must be created in advance. See [this](https://docs.docker.com/engine/reference/commandline/network_create/) for more information on how to do this. The default benchmarks include examples of this specification. Further, the path where the volume is mounted within the service (as specified by the `volumes` service subsection in the compose file) should be noted. 

The snippet below indicates the boilerplate code of a benchmark Docker compose file:
```yaml
version: "3.9"
services:
  <benchmark_name>:
    ...
    environment:
      - PROMETHEUS_TARGET_PORT=${PROMETHEUS_TARGET_PORT}
    networks:
      - HelioBench-network
    volumes:
      - HelioBench:/home/experiment # Remember this path - it is where finish files will be written.
...
volumes:
  HelioBench:
    external: true

networks:
  HelioBench-network:
    external: true
```

Finally, in order for the target metric exporter process to be accessible by Prometheus, a port should be given to specify the communication channel. Therefore, the `PROMETHEUS_TARGET_PORT` variable should be included in order to signify this.

### 2. Install and run Node exporter
For Prometheus to gather metrics for benchmarked services, the Node exporter should be ran at the benchmarked service in order to export metrics first. In multi-service benchmarks, it is important that the exporter is ran **on the benchmarked service**, rather than the workload or utility service. Otherwise, inaccurate metrics will be gathered.

The example below showcases installing Node Exporter on Ubuntu 16.04 Docker image:
```dockerfile
# Install Node explorer
RUN wget https://github.com/prometheus/node_exporter/releases/download/v1.2.2/node_exporter-1.2.2.linux-amd64.tar.gz
RUN tar xvfz node_exporter-1.2.2.linux-amd64.tar.gz
```
This may need to be changed depending on the type of Docker image used. For more information on how to install the node exporter, see [this](https://prometheus.io/docs/guides/node-exporter/).

Finally, within the Docker startup command, specified either in the Dockerfile or the Docker compose file, the Node exporter service must be run in the background. Further, its listening port should be specified over the variable set in Step 2. For example:
```bash
cd ./node_exporter-1.2.2.linux-amd64 && ./node_exporter --web.listen-address=":$PROMETHEUS_TARGET_PORT" &
```
Once this is ran, the benchmarked service could be started as normal. See [this](https://prometheus.io/docs/guides/node-exporter/) for more information about the `node_exporter` command and its parameters.

### 3. Finish with a "finish file"
In order for HelioBench to detect that benchmarks have completed, a "finish file" must be created within the storage specified in Step 1. The file contents do not matter. However, its name must be in the `$EXPERIMENT_WORKLOAD.finish` format. Remember that the `$EXPERIMENT_WORKLOAD` environment variable is automatically exported for each benchmark. An example of creating a finish file could be:
```bash
# Create a file to indicate finish
touch /home/experiment/$EXPERIMENT_WORKLOAD.finish
```

When a finish file is seen by the orchestrator, the benchmark will be considered to be completed. Therefore, its process will be stopped and its metrics collected.


## Cloud Experiment Benchmark Integration Guide
In order to add support for Azure ACI deployment, a benchmark should include a `deployment.yml` file which is an extension to its `docker-compose` specification. This guide will walk through all relevant steps in creating this file from a compose specification. Further, all benchmarks in the HelioBench suite support ACI deployment. Hence, their configurations could be used as examples. See [this](https://docs.docker.com/cloud/aci-compose-features/) for an exhaustive reference of this configuration.

### 1. Correct image
As part of deployment orchestration, HelioBench will push all required images into an Azure Container Registry (ACR). Therefore, in order to access the correct image for deployment, the full URL of a given image should be specified within the `deployment.yml` file. This could be done through `azure` environment variables (see above). The following line is an example of such specification:
```yaml
image: ${AZURE_CONTAINER_REGISTRY}.azurecr.io/${EXPERIMENT_WORKLOAD}-${EXPERIMENT_WORKLOAD}:latest
```

For multi-service deployments, different images may be needed for services. See `go-api` for such example.

### 2. Correct volume
Much like in local experiments, HelioBench requires a volume shared between all benchmarks in order to coordinate finish files. In the deployment case, an Azure File Storage entity must be specified for a volume. This is done by the following configuration:
```yaml
    volumes:
      - heliobench:/home/experiment
...
volumes:
  heliobench:
    driver: azure_file
    driver_opts:
      share_name: ${AZURE_FILE_SHARE_NAME}
      storage_account_name: ${AZURE_STORAGE_ACCOUNT_NAME}
```
This is similar to the `docker-compose` specfication, however, it makes use of more parameters, which could be specfied as environment variables. Remember, the `azure` and `enviroment` sections of the `experiment.yml` file are included within the process of each benchmark, therefore, they are reachable by the `deployment.yml` configuration.

### 3. Correct resource specifications
Each ACI needs to be allocated specific services. Therefore, each service within the `deployment.yml` file should include a resource specification. Once again, HelioBench environment variables, specified at the top-level `experiment.yml` file, could be used.
```yaml
    deploy:
      resources:
        reservations:
          cpus: ${ALEXNET_NUM_CPUS}
          memory: ${ALEXNET_NUM_RAM}
        limits:
          cpus: ${ALEXNET_CPU_LIMIT}
          memory: ${ALEXNET_RAM_LIMIT}
```

### 4. Domain name
It may not be required to provide a domain name of the ACI as it may be computed automatically. However, on condition that the same benchmark is created within different subscription, the domain name would clash. Hence, it should be specified in such cases. For more information, see [this](https://docs.docker.com/cloud/aci-compose-features/).
```yaml
    domainname: ${DOMAIN_NAME}
```