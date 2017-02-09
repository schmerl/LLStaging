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
## something we haven't written yet goes here if you want to mock up the LL env
./run-cp1.sh
```

and wait until you see `odom received!` in one of the info messages in the
output. Then, from either the host machine or inside the vagrant guest,
you can access the REST communications API with standard HTTP requests that
meet the API from the wiki on port 5000. For example, at a new terminal,

```
% curl -H "Content-Type:application/json" -X POST -d '{}' localhost:5000/action/start
{"ARGUMENTS": {}, "TIME": "2017-01-27T22:51:49.938773"}
%
```

will start the simulation. You can see the debugging output in the terminal
that's running `vagrant ssh` into the guest machine, or issue futher HTTP
requests per the REST API. Here are some example curl requests for different
parts of the API:

```
curl -H "Content-Type:application/json" -X POST -d '{}' localhost:5000/action/start
curl -H "Content-Type:application/json" localhost:5000/action/observe
curl -H "Content-Type:application/json" -X POST -d '{"TIME" : "2017-02-09T21:25:59.332087", "ARGUMENTS" : {"x" : 19.5, "y" : 58.5}}' localhost:5000/action/place_obstacle
```
