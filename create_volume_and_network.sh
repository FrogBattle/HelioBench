#!/bin/bash
# Use this script by executing `./create_volume_and_network.sh <Docker_Storage_Name> <Docker_Volume_Name`

docker context use default

docker network create -d bridge ${1:-"HelioBench-network"}
echo "Created Docker network ${1:-"HelioBench-network"}"

docker volume create ${2:-"HelioBench"}
echo "Created Docker volume ${2:-"HelioBench"}"
