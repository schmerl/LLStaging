#!/bin/bash

#Start the headless XServer
Xorg -noreset +extension GLX +extension RANDR +extension RENDER -logfile ./1.log -config ./xorg.conf :1 & export X_PID=$!

# Method to kill the X-Server when Ctrl-C is pressed
killX() {
  echo "Ctrl-C pressed - killing headless server with pid $X_PID";
  kill -9 $X_PID
  exit 1
}

trap killX INT

export DISPLAY=:1
source /opt/ros/indigo/setup.bash
cd catkin_ws
source devel/setup.bash

export ROS_LOG_DIR=/test/roslog

if [ `grep CP2 /test/data` ]
then
    ## todo: calibration_watcher here
    roslaunch cp_gazebo cp2.launch
else
    ## if /test/data is garbage, brasscomms will pick it up and report the
    ## error to the right place, even in the CP2 case.
    roslaunch cp_gazebo cp1.launch
fi
