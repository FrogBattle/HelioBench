#!/bin/bash

# TODO: Add multistage builds to make this happen properly. See #2.
# bash /home/scripts/setup_experiment.sh

# HelioBench experiment setup
mkdir -p /home/experiment
rm -f /home/experiment/finished/$EXPERIMENT_WORKLOAD.finish

# Perform experiment
ab -n $NUM_REQUESTS -c $NUM_CLIENTS nginx-web:80/heaviest

# TODO: Add multistage builds to make this happen properly. See #2.
# bash /home/scripts/teardown_experiment.sh

# Create a file to indicate finish
touch /home/experiment/$EXPERIMENT_WORKLOAD.finish