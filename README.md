# HelioBench
HelioBench is an automatatically orchestrated microservice benchmarking suite. It allows for the orchestrated run of benchmark services in local Docker containers or in the cloud.

## Running HelioBench
### Virtual Environment
Before running the project, you need to make sure that you have created a virtual environment. Follow the steps below to create one and activate it:
1. Make sure you have at least **Python 3.9** installed. 
2. Create a virtual environment using `python3 -m venv ./venv` at the project root. 
3. Install all project requirements by running `pip3 install -r requirements.txt` from the project root directory.
4. Activate the vritual environment running `source ./venv/bin/activate` for UNIX users or `venv\Scripts\activate.bat` for Windows users.

### Running local 
The main configuration file HelioBench uses is `experiment.yml`. In order to run local experiments, make sure that `DEPLOYMENT=False` is set or the variable is commented out.

The default configuratio of HelioBench runs a Go API benchmark for several minutes. To run this, execute `python3 orchestrator.py`. This is the main command for running HelioBench.

In order to run other benchmarks, the `experiment.yml` file should be changed. The experiment file has the following sections:
- `services`. This section concerns service configurations to be run. Much like `docker-compose` files, it lists services by **specifying their name** as in the `./microservices` folder. Within each service configuration, environment variables can be specified. They are exported into processes which build and create Docker containers. As such, they can be used within container specifications. For example, `GO_API_WEB_PORT` is specified under the `go-api` clause. It is then used within the `deployment.yml` file to map the same port specified within the `experiment.yml` file. The `EXPERIMENT_WORKLOAD` environment variable is automatically exported to each benchmark and contains its name, eg: `go-api` for the Go API benchmark.
- `environment`. This section specifies experiment-wide environment settings. For example, the central Prometheus service port or whether a deployed experiment is perforemed. These variables are all exported into each service as well. For a full description of all possible settings see below.
- `azure`. This section concerns settings relevant to cloud deployed services via Azure ACI. See all available settings below.

### Changing the experiment environment
Below are all possible settings for the `enviroment` section of `experiment.yml`:
| Environment Setting       | Description                                                               | Required?                               |
|---------------------------|---------------------------------------------------------------------------|-----------------------------------------|
| `PROMETHEUS_PORT`         | The Azure subscription all entities are created within.                   | Optional. Defaults to `9090`.           |
| `STOP_PROMETHEUS`         | The Azure resource group of all entities created for experiment purposes. | Optional. Defaults to `True`.           |
| `DEPLOYMENT`              | The Azure CR where to publish and pull Docker images for experiments.     | Optional. Defaults to `False`.          |
| `DEPLOYMENT_COMPOSE_FILE` | ACR username for authentication and creation of container instances.      | Optional. Defaults to `deployment.yml`. |

### Cloud - Azure ACIs
Additional configuration required in `experiment.yml` includes setting `DEPLOYMENT=True` in the `environment` section and popualting all relevant configuration regarding Azure entities.

**Note**: If you need to create all Azure entities for running HelioBench, the automated scripts in `./azure_utilities` could help you. Set configurations within each script or environment variables and execute them by running `./{script_name}` to create relevant entities.

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
| `AZURE_TENANT_ID`                   | This is required when having more than one Azure Directories. It specifies within which directory HelioBench should operate. | Optional. |

After setting all required configurations, HelioBench should run successfully by running `python3 orchestrator.py` as usual.