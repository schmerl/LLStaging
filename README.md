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

After this, the workflow shouldn't change. So, you you add a .deb file to
installation/debs, then git push should call the lfs hooks and work automagically.

**Installation**

Vagrant installation can be found at: https://www.vagrantup.com/docs/installation/

In order to run the simulation, once you've installed vagrant, etc.:

```
vagrant up
vagrant ssh
./run-cp1.sh
```

and wait until you see `odom received!` in one of the info messages in the
output. Then, from either the host machine or inside the vagrant guest,
you can access the REST communications API with standard HTTP requests that
meet the API from the wiki on port 5000. For example, at a new terminal,

```
% curl -X POST -d "" localhost:5000/phase1/power/start_challenge_problem
starting challenge problem
%
```

will start the simulation. You can see the debugging output in the terminal
that's running `vagrant ssh` into the guest machine, or issue futher HTTP
requests per the REST API.
