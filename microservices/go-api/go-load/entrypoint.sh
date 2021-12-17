#!/bin/sh

# Reference: https://github.com/instana/robot-shop/tree/master/load-gen


### HelioBench: Experiment setup
mkdir -p /home/experiment
rm -f /home/experiment/finished/go-api.finish


if [ -z "$HOST" ]
then
    echo "HOST env not set"
    exit 1
fi

if echo "$NUM_CLIENTS" | egrep -q '^[0-9]+$'
then
    if [ $NUM_CLIENTS -eq 0 ]
    then
        NUM_CLIENTS=1
    fi
    echo "Starting load with $NUM_CLIENTS clients"
else
    echo "NUM_CLIENTS $NUM_CLIENTS is not a number"
    exit 1
fi


if [ "$RUN_TIME" != "0" ]
then
    if echo "$RUN_TIME" | egrep -q '^([0-9]+h)?([0-9]+m)?$'
    then
        TIME="-t $RUN_TIME"
    else
        echo "Wrong time format, use 2h42m"
        exit 1
    fi
else
    unset RUN_TIME
    unset TIME
fi

echo "Starting $CLIENTS clients for ${RUN_TIME:-ever}"
if [ "$SILENT" -eq 1 ]
then
    locust -f go-api.py --host "$HOST" --headless -r 1 -u $NUM_CLIENTS $TIME > /dev/null 2>&1
else
    locust -f go-api.py --host "$HOST" --headless -r 1 -u $NUM_CLIENTS $TIME
fi

### HelioBench: Indicate experiment finish
touch /home/experiment/go-api.finish