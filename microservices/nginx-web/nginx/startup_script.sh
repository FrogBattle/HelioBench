#!/bin/bash

# Start the first process


cd ./node_exporter-1.2.2.linux-amd64 && ./node_exporter --web.listen-address=":$PROMETHEUS_TARGET_PORT" &
nginx

# Wait for any process to exit
wait -n
  
# Exit with status of process that exited first
exit $?
