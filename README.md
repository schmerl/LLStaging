cmu-robotics
============

**Important note**: This repository uses Git LFS and Git Submodules so the workflow for interacting with
this repo is very different.

**Git:** In order for Git LFS to work properly, you must have a modern version of git. This is known to work with 2.11.0 and to fail around 2.5.?, but we don't know where the exact threshold is.

**Git LFS:**  Install Git LFS (https://git-lfs.github.com/).

To check out the files you need to do the following:
```
git lfs install (This should only be done once)
git clone ...
git lfs pull
```

**Submodules**:

`brasscomms` (`installation/catkin_ws/src/brasscomms`) and `rainbow-brass` (`installation/das/rainbow-brass`) 
are git submodules. 

The first time you pull from this repo, you will need to run `git submodule init` 
and `git submodule update` from within these directories, to pupulate them. 

You will also need to 
run `git pull origin master` in each of these directories **every time you want to pull the latest 
version of those repositories**.

After this, the workflow shouldn't change. So, you you add a .deb file to
installation/debs, then git push should call the lfs hooks and work automagically.

**Installation**

You need to install Vagrant (https://www.vagrantup.com/docs/installation/), and VirtualBox (https://www.virtualbox.org/wiki/Downloads)
After installing Vagrant and Virtualbox and pulling from github, run the simulation by:

```
cd installation ## from within the LLStaging directory on your local machine
vagrant up
vagrant ssh
./mockup.sh ## if you aren't MIT/LL but want the config and log to work
./start.sh
```
and wait until you see `odom received!` in one of the info messages in the
output. Then, from either the host machine or inside the vagrant guest,
you can access the REST communications API with standard HTTP requests that
meet the API from the wiki on port 5000. For example, at a new terminal,

```
% curl -H "Content-Type:application/json" -X POST -d '{"TIME" : "2017-02-09T21:25:59.332087", "ARGUMENTS" : {}}' localhost:5000/action/start
%
```

will start the simulation. Note that the `mockup.sh` script places the simple JSON config file from our wikipage to `/test/data`. You will need to edit that file to induce different test conditions, as well as use `curl` to perturb or observe the test as it's running.

You can see the debugging output in a few places:

* the terminal that's running `vagrant ssh` into the guest machine

* the ROS log files, in `/test/roslog/latest/*`

* the mocked-up log file shared with the TH, at `/test/log`

* the terminal that you're running `curl` commands from

Some example curl requests for the different endpoints given in the API,
are found in `smoke.sh`, which you can run from the guest machine to smoke
test the end points. That script gives the examples in wiki page order,
which might not be the order that you would call them in a real use case.

**Running tests**

When thinking about doing a test, you should be aware of a couple of things:

1. Only action/set_battery and action/place_obstacle are pertinent in CP1.

2. LL are only going to place an obstacle before the test starts.

3. You can get the initial path that the robot is to travel by invoking action/query_path. This gives you a set of waypoints that the robot will pass.

4. place_obstacle takes coordinates, and you can find the mapping of waypoints and coordinates here: https://github.com/schmerl/LLStaging/blob/master/installation/catkin_ws/src/cp_gazebo/maps/Wean-entire-floor4-waypoint-locations.json (node-id == waypoint)

5. Interesting tests are where CP1_NoAdaptation fails and CP1_Adaptation doesn't. If CP1_NoAdaptation succeeds (i.e, the robot gets to its target), then LL will not run the CP1_Adaptation on that case. So try to keep that in mind when thinking about perturbations.

6. It would be interesting to have pairs of runs - CP1_NoAdaptation and CP1_Adaptation on the same perturbation
