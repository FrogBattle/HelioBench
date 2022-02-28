#!/bin/bash
# Src: https://docs.microsoft.com/en-us/cli/azure/group?view=azure-cli-latest
# WARNING: Make sure you are logged into the correct directory.

# Change these four parameters as needed
RESOURCE_GROUP_NAME=HB-Test2
RESOURCE_GROUP_LOCATION=ukwest

az group create -l $RESOURCE_GROUP_LOCATION -n $RESOURCE_GROUP_NAME 