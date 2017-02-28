#! /bin/bash

# permissions hacks to deal with mystery losing exec
cd catkin_ws/
find . -name "*.py" | xargs chmod +x
find . -name "*.sh" | xargs chmod +x
chmod +x /home/vagrant/bin/*
cd ../
chmod +x *.sh
source /opt/ros/indigo/setup.bash
cd catkin_ws/src
catkin_init_workspace
cd ..
catkin_make
