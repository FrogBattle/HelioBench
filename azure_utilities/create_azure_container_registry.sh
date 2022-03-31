#!/bin/bash
# Reference: https://docs.microsoft.com/en-us/azure/container-registry/container-registry-get-started-azure-cli
# WARNING: Make sure you are logged into the correct directory.

# Change these four parameters as needed
ACR_NAME=helioregistry2
ACR_RESOURCE_GROUP=HB-Test2

az acr create \
    --resource-group $ACR_RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic

az acr update \
    -n $ACR_NAME \
    --admin-enabled true

az acr login \
    --name $ACR_NAME

az acr credential show \
    --name $ACR_NAME
