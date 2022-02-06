#!/bin/sh

# Reference: https://github.com/instana/robot-shop/tree/master/load-gen


### HelioBench: Experiment setup
mkdir -p /home/experiment
rm -f /home/experiment/finished/go-api.finish


if [ -z "$GO_LOAD_TARGET_HOST" ]
then
    echo "GO_LOAD_TARGET_HOST env not set"
    exit 1
fi

if echo "$GO_LOAD_NUM_CLIENTS" | egrep -q '^[0-9]+$'
then
    if [ $GO_LOAD_NUM_CLIENTS -eq 0 ]
    then
        GO_LOAD_NUM_CLIENTS=1
    fi
    echo "Starting load with $GO_LOAD_NUM_CLIENTS clients"
else
    echo "GO_LOAD_NUM_CLIENTS $GO_LOAD_NUM_CLIENTS is not a number"
    exit 1
fi


if [ "$GO_LOAD_RUN_TIME" != "0" ]
then
    if echo "$GO_LOAD_RUN_TIME" | egrep -q '^([0-9]+h)?([0-9]+m)?$'
    then
        TIME="-t $GO_LOAD_RUN_TIME"
    else
        echo "Wrong time format, use 2h42m"
        exit 1
    fi
else
    unset GO_LOAD_RUN_TIME
    unset TIME
fi

echo "Starting $CLIENTS clients for ${GO_LOAD_RUN_TIME:-ever}"
if [ "$SILENT" -eq 1 ]
then
    locust -f go-api.py --host "$GO_LOAD_TARGET_HOST" --headless -r 1 -u $GO_LOAD_NUM_CLIENTS $TIME > /dev/null 2>&1
else
    locust -f go-api.py --host "$GO_LOAD_TARGET_HOST" --headless -r 1 -u $GO_LOAD_NUM_CLIENTS $TIME
fi

### HelioBench: Indicate experiment finish
touch /home/experiment/go-api.finish