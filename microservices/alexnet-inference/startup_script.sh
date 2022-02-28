#!/bin/bash

# Start the first process

cd ./node_exporter-1.2.2.linux-amd64 && ./node_exporter --web.listen-address=":$PROMETHEUS_TARGET_PORT" &

# HelioBench experiment setup
mkdir -p /home/experiment
rm -f /home/experiment/finished/$EXPERIMENT_WORKLOAD.finish

python3 run_alexnet.py

# Create a file to indicate finish
touch /home/experiment/$EXPERIMENT_WORKLOAD.finish

# Wait for any process to exit
wait -n
  
# Exit with status of process that exited first
exit $?
