cmu-robotics
============

In order to run the simulation, once you've installed vagrant, etc.:

```
vagrant up
vagrant ssh
./run-cp1.sh
```

then, from either the host machine or inside the vagrant guest, you can
access the REST communications API with standard HTTP requests that meet
the API from the wiki on port 5000. For example, at a new terminal,

```
% curl -X POST -d "" localhost:5000/phase1/power/start_challenge_problem
starting challenge problem
%
```

will start the simulation. You can see the debugging output in the terminal
that's running `vagrant ssh` into the guest machine, or issue futher HTTP
requests per the REST API.
