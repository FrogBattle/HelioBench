#!/bin/bash

cd ./node_exporter-1.2.2.linux-amd64 && ./node_exporter &
memcached -p 11211 -v -d

# Wait for any process to exit
wait -n
  
# Exit with status of process that exited first
exit $?