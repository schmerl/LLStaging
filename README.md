cmu-robotics
============

**Note about LFS**: This repository uses Git LFS for large file storage (https://git-lfs.github.com/).
This needs to be installed on the pulling machine, and it changes the workflow slightly.

To check out the files you need to do the following:
```
git lfs install (This should only be done once)
git clone ...
git lfs pull
```

`brasscomms` is a git submodule, so you will need to run `git submodule init` and `git submodule update` to populate that directory.

After this, the workflow shouldn't change. So, you you add a .deb file to
installation/debs, then git push should call the lfs hooks and work automagically.

**Installation**

Vagrant installation can be found at: https://www.vagrantup.com/docs/installation/

In order to run the simulation, once you've installed vagrant, etc.:

```
vagrant up
vagrant ssh
./setup-cp1.sh
./mockup.sh ## if you aren't MIT/LL but want the config and log to work
./run-cp1.sh
```

and wait until you see `odom received!` in one of the info messages in the
output. Then, from either the host machine or inside the vagrant guest,
you can access the REST communications API with standard HTTP requests that
meet the API from the wiki on port 5000. For example, at a new terminal,

```
% curl -H "Content-Type:application/json" -X POST -d '{"TIME" : "2017-02-09T21:25:59.332087", "ARGUMENTS" : {}}' localhost:5000/action/start
{"ARGUMENTS": {}, "TIME": "2017-01-27T22:51:49.938773"}
%
```

will start the simulation.

You can see the debugging output in a few places:

* the terminal that's running `vagrant ssh` into the guest machine

* the ROS log files, usually in `~/.ros/log/latest/*`

* the mocked-up log file shared with the TH, at `/test/log`

Some example curl requests for the different endpoints given in the API,
are found in `smoke.sh`, which you can run from the guest machine to smoke
test the end points. That script gives the examples in wiki page order,
which might not be the order that you would call them in a real use case.
