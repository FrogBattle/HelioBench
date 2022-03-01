#!/bin/bash
# Src: https://docs.microsoft.com/en-us/azure/container-instances/container-instances-volume-azure-files
# WARNING: Make sure you are logged into the correct directory.

# Change these four parameters as needed
ACI_PERS_RESOURCE_GROUP=HB-Test2
ACI_PERS_STORAGE_ACCOUNT_NAME=heliostorage$RANDOM
ACI_PERS_LOCATION=ukwest
ACI_PERS_SHARE_NAME=heliofileshare2


# Create the storage account with the parameters
az storage account create \
    --resource-group $ACI_PERS_RESOURCE_GROUP \
    --name $ACI_PERS_STORAGE_ACCOUNT_NAME \
    --location $ACI_PERS_LOCATION \
    --sku Standard_LRS

# Create the file share
az storage share create \
  --name $ACI_PERS_SHARE_NAME \
  --account-name $ACI_PERS_STORAGE_ACCOUNT_NAME

STORAGE_KEY=$(az storage account keys list --resource-group $ACI_PERS_RESOURCE_GROUP --account-name $ACI_PERS_STORAGE_ACCOUNT_NAME --query "[0].value" --output tsv)

echo 'Your storage key is:' $STORAGE_KEY