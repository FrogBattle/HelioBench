#!/bin/bash

# TODO: Add multistage builds to make this happen properly. See #2.
# bash /home/scripts/setup_experiment.sh

# HelioBench experiment setup
mkdir -p /home/experiment
rm -f /home/experiment/finished/$EXPERIMENT_WORKLOAD.finish

# Perform experiment
./libmemcached-1.0.18/clients/memaslap --servers=$SERVERS -t $TIME -S $STAT_FREQ --threads=8 --concurrency=128 --cfg_cmd=./.memaslap.cnf

# TODO: Add multistage builds to make this happen properly. See #2.
# bash /home/scripts/teardown_experiment.sh

# Create a file to indicate finish
touch /home/experiment/$EXPERIMENT_WORKLOAD.finish