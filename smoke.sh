#!/bin/bash

echo "query path"
curl localhost:5000/action/query_path

echo "start"
curl -H "Content-Type:application/json" -X POST -d '{"TIME" : "2017-02-09T21:25:59.332087", "ARGUMENTS" : {}}' localhost:5000/action/start

echo "observe"
curl localhost:5000/action/observe

echo "set battery"
curl -H "Content-Type:application/json" -X POST -d '{"TIME" : "2017-02-09T21:25:59.332087", "ARGUMENTS" : {"voltage" : 120}}' localhost:5000/action/set_battery

echo "place obstacle"
curl -H "Content-Type:application/json" -X POST -d '{"TIME" : "2017-02-09T21:25:59.332087", "ARGUMENTS" : {"x" : 19.5, "y" : 11.5}}' localhost:5000/action/place_obstacle

echo "remove obstacle"
curl -H "Content-Type:application/json" -X POST -d '{"TIME" : "2017-02-09T21:25:59.332087", "ARGUMENTS" : {"obstacleid" : "Obstacle_0"}}' localhost:5000/action/remove_obstacle

echo "perturb sensor"
curl -H "Content-Type:application/json" -X POST -d '{"TIME" : "2017-02-09T21:25:59.332087", "ARGUMENTS" : {"bump" : {"x" : 0, "y": 0, "z" : 0, "p" : 0, "w" : 0, "r" : 0}}}' localhost:5000/action/perturb_sensor
