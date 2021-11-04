#!/bin/bash
echo "Measuring docker containers [ hit CTRL+C to stop]"
for (( ; ; ))
do
   docker stats $(docker ps -q) --no-stream --no-trunc --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemPerc}}\t{{.MemUsage}}\t{{.BlockIO}}\t{{.NetIO}}" 
   sleep 1s
done