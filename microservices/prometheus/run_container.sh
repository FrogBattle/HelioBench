#!/bin/bash

docker run \
    -d -p 9090:9090 \
    --name helio-prometheus \
    --network HelioBench-network \
    helio-prometheus \
    --config.file=/etc/prometheus/prometheus.yml \
    --web.listen-address=:9090