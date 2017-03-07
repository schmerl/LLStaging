#! /bin/bash

# permissions hacks to deal with mystery losing exec
sudo find . -name "*.py" | xargs sudo chmod +x
sudo find . -name "*.sh" | xargs sudo chmod +x
chmod +x /home/vagrant/bin/*

source /opt/ros/indigo/setup.bash
cd catkin_ws/src
catkin_init_workspace
cd ..
catkin_make
