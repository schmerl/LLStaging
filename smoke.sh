#!/bin/bash

echo "query path"
curl localhost:5000/action/query_path
echo
echo

echo "start"
curl -H "Content-Type:application/json" -X POST -d '{"TIME" : "2017-02-16T17:35:39.539Z", "ARGUMENTS" : {}}' localhost:5000/action/start
echo
echo

echo "observe"
curl localhost:5000/action/observe
echo
echo

echo "set battery"
curl -H "Content-Type:application/json" -X POST -d '{"TIME" : "2017-02-16T17:35:39.539Z", "ARGUMENTS" : {"voltage" : 120}}' localhost:5000/action/set_battery
echo
echo

echo "place obstacle"
curl -H "Content-Type:application/json" -X POST -d '{"TIME" : "2017-02-16T17:35:39.539Z", "ARGUMENTS" : {"x" : 19.5, "y" : 11.5}}' localhost:5000/action/place_obstacle
echo
echo

echo "remove obstacle"
curl -H "Content-Type:application/json" -X POST -d '{"TIME" : "2017-02-16T17:35:39.539Z", "ARGUMENTS" : {"obstacleid" : "Obstacle_0"}}' localhost:5000/action/remove_obstacle
echo
echo

echo "perturb sensor"
curl -H "Content-Type:application/json" -X POST -d '{"TIME" : "2017-02-16T17:35:39.539Z", "ARGUMENTS" : {"bump" : {"x" : 0, "y": 0, "z" : 0, "p" : 0, "w" : 0, "r" : 0}}}' localhost:5000/action/perturb_sensor
echo
echo
