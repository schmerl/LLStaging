#!/bin/bash

## this script mocks up some of the things in the API for the log and
## config file locations. you should run it because brasscomms will
## crash otherwise, but it should never be added to an automated
## provisioning process: depending on order of operations it may well
## clobber things in the actual test environment.

sudo mkdir -p /test
sudo chown vagrant /test
cp /home/vagrant/catkin_ws/src/cp_gazebo/ex_config.json /test/data
touch /test/log
