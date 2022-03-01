# HelioBench
HelioBench is an automatatically orchestrated microservice benchmarking suite. It allows for the orchestrated run of benchmark services in local Docker containers or in the cloud.

## Running HelioBench
### Virtual Environment
Make sure you have installed at least **Python 3.9**, create a virtual environment using `pip3 -m venv ./venv` and install all project requirements by running `pip3 install -r requirements.txt` from the project root directory.

### Local run

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